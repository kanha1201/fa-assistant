"""Main data ingestion script."""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.extractors import (
    extract_eternal_q2_report,
    scrape_eternal_data,
    scrape_sector_data,
    scrape_eternal_moneycontrol,
    scrape_zomato_groww
)
from src.storage import db, file_storage, vector_store
from src.processors import text_cleaner, data_validator
from src.utils import logger, settings
import uuid


def ingest_pdf_report():
    """Ingest PDF quarterly report."""
    logger.info("=" * 80)
    logger.info("Starting PDF Report Ingestion")
    logger.info("=" * 80)
    
    try:
        # Extract PDF content
        pdf_data = extract_eternal_q2_report()
        
        # Save to file storage
        saved_paths = file_storage.save_extraction_result(
            source="pdf_q2_fy26",
            data=pdf_data,
            company_symbol="ETERNAL"
        )
        
        # Get or create company
        company = db.get_or_create_company(
            symbol="ETERNAL",
            name="Eternal Limited (Formerly Zomato Limited)",
            sector="Online Services"
        )
        
        # Clean and validate text
        cleaned_text = text_cleaner.clean_text(pdf_data["text"])
        cleaned_text = data_validator.sanitize_text(cleaned_text)
        
        # Save document to database
        document = db.save_document(
            company_id=company.id,
            document_type="quarterly_report",
            source_url=pdf_data["source_url"],
            content_text=cleaned_text,
            metadata={
                "total_pages": pdf_data["metadata"]["total_pages"],
                "total_images": pdf_data["metadata"]["total_images"],
                "images_with_text": pdf_data["metadata"]["images_with_text"],
                "file_path": str(saved_paths.get("json", ""))
            },
            file_path=str(saved_paths.get("json", ""))
        )
        
        # Add to vector store (chunk text for better retrieval)
        chunks = text_cleaner.chunk_text(cleaned_text, chunk_size=1000, overlap=200)
        chunk_ids = []
        
        for i, chunk in enumerate(chunks):
            chunk_id = f"{document.id}_{i}"
            chunk_ids.append(chunk_id)
            
            vector_store.add_documents(
                texts=[chunk],
                metadatas=[{
                    "document_id": str(document.id),
                    "company_symbol": "ETERNAL",
                    "document_type": "quarterly_report",
                    "chunk_index": i,
                    "source": "pdf_q2_fy26"
                }],
                ids=[chunk_id]
            )
        
        # Update document with embedding IDs
        session = db.get_session()
        try:
            # Re-query document to update it
            from src.storage.database import Document
            doc = session.query(Document).filter_by(id=document.id).first()
            if doc:
                doc.embedding_id = ",".join(chunk_ids)
                session.commit()
        finally:
            session.close()
        
        logger.info(f"✓ PDF ingestion complete. Saved {len(chunks)} chunks to vector store")
        return True
        
    except Exception as e:
        logger.error(f"✗ PDF ingestion failed: {e}", exc_info=True)
        return False


def ingest_screener_data():
    """Ingest Screener.in data."""
    logger.info("=" * 80)
    logger.info("Starting Screener.in Data Ingestion")
    logger.info("=" * 80)
    
    try:
        # Scrape company data
        screener_data = scrape_eternal_data()
        
        # Validate data
        if not data_validator.validate_company_data(screener_data):
            logger.warning("Screener data validation failed, but continuing...")
        
        # Save to file storage
        saved_paths = file_storage.save_extraction_result(
            source="screener",
            data=screener_data,
            company_symbol="ETERNAL"
        )
        
        # Get or create company
        company = db.get_or_create_company(
            symbol="ETERNAL",
            name=screener_data.get("company_name", "Eternal Limited"),
            sector="Online Services"
        )
        
        # Extract and save financial metrics
        if "key_metrics" in screener_data:
            for metric_name, metric_value in screener_data["key_metrics"].items():
                try:
                    # Try to parse numeric value
                    numeric_value = None
                    if metric_value:
                        # Remove commas and try to parse
                        clean_value = str(metric_value).replace(",", "").strip()
                        if clean_value and clean_value != "-":
                            try:
                                numeric_value = float(clean_value)
                            except ValueError:
                                pass
                    
                    if numeric_value is not None:
                        db.save_financial_metric(
                            company_id=company.id,
                            metric_name=data_validator.normalize_company_symbol(metric_name),
                            metric_value=numeric_value,
                            source="screener"
                        )
                except Exception as e:
                    logger.warning(f"Failed to save metric {metric_name}: {e}")
        
        # Save document for RAG
        full_text = screener_data.get("full_text", "")
        cleaned_text = text_cleaner.clean_text(full_text)
        cleaned_text = data_validator.sanitize_text(cleaned_text)
        
        if cleaned_text:
            document = db.save_document(
                company_id=company.id,
                document_type="screener_data",
                source_url=screener_data["source_url"],
                content_text=cleaned_text,
                metadata={
                    "key_metrics": screener_data.get("key_metrics", {}),
                    "ratios": screener_data.get("ratios", {})
                }
            )
            
            # Add to vector store
            chunks = text_cleaner.chunk_text(cleaned_text, chunk_size=1000, overlap=200)
            chunk_ids = []
            
            for i, chunk in enumerate(chunks):
                chunk_id = f"{document.id}_{i}"
                chunk_ids.append(chunk_id)
                
                vector_store.add_documents(
                    texts=[chunk],
                    metadatas=[{
                        "document_id": str(document.id),
                        "company_symbol": "ETERNAL",
                        "document_type": "screener_data",
                        "chunk_index": i,
                        "source": "screener"
                    }],
                    ids=[chunk_id]
                )
            
            document.embedding_id = ",".join(chunk_ids)
            session = db.get_session()
            try:
                session.commit()
            finally:
                session.close()
        
        logger.info("✓ Screener.in ingestion complete")
        return True
        
    except Exception as e:
        logger.error(f"✗ Screener.in ingestion failed: {e}", exc_info=True)
        return False


def ingest_moneycontrol_data():
    """Ingest MoneyControl data."""
    logger.info("=" * 80)
    logger.info("Starting MoneyControl Data Ingestion")
    logger.info("=" * 80)
    
    try:
        # Scrape MoneyControl data
        moneycontrol_data = scrape_eternal_moneycontrol()
        
        # Save to file storage
        saved_paths = file_storage.save_extraction_result(
            source="moneycontrol",
            data=moneycontrol_data,
            company_symbol="ETERNAL"
        )
        
        # Get or create company
        company = db.get_or_create_company(
            symbol="ETERNAL",
            name=moneycontrol_data.get("company_name", "Eternal Limited"),
            sector="Online Services"
        )
        
        # Save document for RAG
        full_text = moneycontrol_data.get("full_text", "")
        cleaned_text = text_cleaner.clean_text(full_text)
        cleaned_text = data_validator.sanitize_text(cleaned_text)
        
        if cleaned_text:
            document = db.save_document(
                company_id=company.id,
                document_type="moneycontrol_data",
                source_url=moneycontrol_data["source_url"],
                content_text=cleaned_text,
                metadata={
                    "price_info": moneycontrol_data.get("price_info", {}),
                    "ratios": moneycontrol_data.get("ratios", {})
                }
            )
            
            # Add to vector store
            chunks = text_cleaner.chunk_text(cleaned_text, chunk_size=1000, overlap=200)
            chunk_ids = []
            
            for i, chunk in enumerate(chunks):
                chunk_id = f"{document.id}_{i}"
                chunk_ids.append(chunk_id)
                
                vector_store.add_documents(
                    texts=[chunk],
                    metadatas=[{
                        "document_id": str(document.id),
                        "company_symbol": "ETERNAL",
                        "document_type": "moneycontrol_data",
                        "chunk_index": i,
                        "source": "moneycontrol"
                    }],
                    ids=[chunk_id]
                )
            
            document.embedding_id = ",".join(chunk_ids)
            session = db.get_session()
            try:
                session.commit()
            finally:
                session.close()
        
        logger.info("✓ MoneyControl ingestion complete")
        return True
        
    except Exception as e:
        logger.error(f"✗ MoneyControl ingestion failed: {e}", exc_info=True)
        return False


def ingest_groww_data():
    """Ingest Groww data."""
    logger.info("=" * 80)
    logger.info("Starting Groww Data Ingestion")
    logger.info("=" * 80)
    
    try:
        # Scrape Groww data
        groww_data = scrape_zomato_groww()
        
        # Save to file storage
        saved_paths = file_storage.save_extraction_result(
            source="groww",
            data=groww_data,
            company_symbol="ETERNAL"
        )
        
        # Get or create company
        company = db.get_or_create_company(
            symbol="ETERNAL",
            name=groww_data.get("stock_name", "Eternal Limited"),
            sector="Online Services"
        )
        
        # Save document for RAG
        full_text = groww_data.get("full_text", "")
        cleaned_text = text_cleaner.clean_text(full_text)
        cleaned_text = data_validator.sanitize_text(cleaned_text)
        
        if cleaned_text:
            document = db.save_document(
                company_id=company.id,
                document_type="groww_data",
                source_url=groww_data["source_url"],
                content_text=cleaned_text,
                metadata={
                    "price_info": groww_data.get("price_info", {}),
                    "metrics": groww_data.get("metrics", {})
                }
            )
            
            # Add to vector store
            chunks = text_cleaner.chunk_text(cleaned_text, chunk_size=1000, overlap=200)
            chunk_ids = []
            
            for i, chunk in enumerate(chunks):
                chunk_id = f"{document.id}_{i}"
                chunk_ids.append(chunk_id)
                
                vector_store.add_documents(
                    texts=[chunk],
                    metadatas=[{
                        "document_id": str(document.id),
                        "company_symbol": "ETERNAL",
                        "document_type": "groww_data",
                        "chunk_index": i,
                        "source": "groww"
                    }],
                    ids=[chunk_id]
                )
            
            document.embedding_id = ",".join(chunk_ids)
            session = db.get_session()
            try:
                session.commit()
            finally:
                session.close()
        
        logger.info("✓ Groww ingestion complete")
        return True
        
    except Exception as e:
        logger.error(f"✗ Groww ingestion failed: {e}", exc_info=True)
        return False


def ingest_sector_data():
    """Ingest sector data."""
    logger.info("=" * 80)
    logger.info("Starting Sector Data Ingestion")
    logger.info("=" * 80)
    
    try:
        # Scrape sector data
        sector_data = scrape_sector_data()
        
        # Save to file storage
        saved_paths = file_storage.save_extraction_result(
            source="sector",
            data=sector_data,
            company_symbol="SECTOR"
        )
        
        # Save document for RAG (no company_id for sector data)
        full_text = sector_data.get("full_text", "")
        cleaned_text = text_cleaner.clean_text(full_text)
        cleaned_text = data_validator.sanitize_text(cleaned_text)
        
        if cleaned_text:
            document = db.save_document(
                company_id=None,
                document_type="sector_data",
                source_url=sector_data["source_url"],
                content_text=cleaned_text,
                metadata={
                    "sector_name": sector_data.get("sector_name", ""),
                    "companies": sector_data.get("companies", []),
                    "benchmarks": sector_data.get("benchmarks", {})
                }
            )
            
            # Add to vector store
            chunks = text_cleaner.chunk_text(cleaned_text, chunk_size=1000, overlap=200)
            chunk_ids = []
            
            for i, chunk in enumerate(chunks):
                chunk_id = f"{document.id}_{i}"
                chunk_ids.append(chunk_id)
                
                vector_store.add_documents(
                    texts=[chunk],
                    metadatas=[{
                        "document_id": str(document.id),
                        "document_type": "sector_data",
                        "chunk_index": i,
                        "source": "screener_sector"
                    }],
                    ids=[chunk_id]
                )
            
            document.embedding_id = ",".join(chunk_ids)
            session = db.get_session()
            try:
                session.commit()
            finally:
                session.close()
        
        logger.info("✓ Sector data ingestion complete")
        return True
        
    except Exception as e:
        logger.error(f"✗ Sector data ingestion failed: {e}", exc_info=True)
        return False


def main():
    """Main ingestion pipeline."""
    logger.info("🚀 Starting Financial Data Ingestion Pipeline")
    logger.info(f"Data will be stored in: {settings.processed_data_path}")
    logger.info(f"Vector DB location: {settings.vector_db_path}")
    
    # Create database tables if they don't exist
    try:
        db.create_tables()
    except Exception as e:
        logger.warning(f"Database table creation: {e}")
        logger.info("Continuing with ingestion...")
    
    results = {}
    
    # Run all ingestion tasks
    results["pdf"] = ingest_pdf_report()
    results["screener"] = ingest_screener_data()
    results["moneycontrol"] = ingest_moneycontrol_data()
    results["groww"] = ingest_groww_data()
    results["sector"] = ingest_sector_data()
    
    # Summary
    logger.info("=" * 80)
    logger.info("INGESTION SUMMARY")
    logger.info("=" * 80)
    
    for source, success in results.items():
        status = "✓ SUCCESS" if success else "✗ FAILED"
        logger.info(f"{source.upper():15} : {status}")
    
    total_documents = vector_store.count()
    logger.info(f"\nTotal documents in vector store: {total_documents}")
    
    successful = sum(results.values())
    total = len(results)
    logger.info(f"\nOverall: {successful}/{total} sources ingested successfully")
    
    if successful == total:
        logger.info("🎉 All data sources ingested successfully!")
    else:
        logger.warning(f"⚠️  {total - successful} source(s) failed. Check logs for details.")


if __name__ == "__main__":
    main()

