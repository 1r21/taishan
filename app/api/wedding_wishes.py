import json
from datetime import datetime

from app.libs.db import db_helper
from app.libs.logger import LoggerHandler
from app.libs.decorator import route
from app.libs.response import Status, show_reponse
from app.libs.variable import request

logger = LoggerHandler("api.wedding_wishes")

# Create wedding messages table if not exists
create_table_sql = """
CREATE TABLE IF NOT EXISTS `wedding_messages` (
    `id` INT(6) NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(50) NOT NULL,
    `message` TEXT NOT NULL,
    `phone` VARCHAR(20) DEFAULT NULL,
    `attending` BOOLEAN DEFAULT FALSE,
    `guests` INT DEFAULT 0,
    `created_at` DATETIME NOT NULL
) ENGINE = InnoDB DEFAULT CHARACTER SET utf8mb4;
"""

try:
    db_helper.execute_commit(create_table_sql)
    logger.info("Wedding messages table created or already exists")
except Exception as e:
    logger.error(f"Failed to create wedding messages table: {e}")


@route("/api/wedding/messages")
def get_wedding_messages():
    """
    Get all wedding messages with pagination
    Query parameters:
    - page: Current page number (default: 1)
    - pageSize: Number of messages per page (default: 20)
    """
    query = request.get("qs")
    default_page = 1
    default_page_size = 20
    page = default_page
    page_size = default_page_size
    
    if query:
        page = int(query.get("page", [default_page])[0])
        page_size = int(query.get("pageSize", [default_page_size])[0])
    
    # Get total count
    total_sql = "SELECT COUNT(*) FROM wedding_messages"
    total = db_helper.fetchone(total_sql)[0]
    
    # Get messages with pagination
    sql = """
    SELECT id, name, message, phone, attending, guests, created_at 
    FROM wedding_messages 
    ORDER BY created_at DESC 
    LIMIT %s OFFSET %s
    """
    
    limit = page_size
    offset = (page - 1) * page_size
    messages = db_helper.execute_sql(sql, (limit, offset))
    
    data = []
    for message in messages:
        id, name, msg_text, phone, attending, guests, created_at = message
        data.append({
            "id": id,
            "name": name,
            "message": msg_text,
            "phone": phone,
            "attending": bool(attending),
            "guests": guests,
            "created_at": created_at.strftime("%Y-%m-%d %H:%M:%S")
        })
    
    return show_reponse(
        data={
            "page": page,
            "pageSize": page_size,
            "total": total,
            "list": data
        }
    )


@route("/api/wedding/message")
def get_wedding_message_by_id():
    """Get a specific wedding message by ID"""
    data = request.get("data")
    if not data:
        return show_reponse(code=Status.other, message="Missing parameters")
    
    message_id = data.get("id")
    if not message_id:
        return show_reponse(code=Status.other, message="Message ID is required")
    
    sql = """
    SELECT id, name, message, phone, attending, guests, created_at 
    FROM wedding_messages 
    WHERE id = %s
    """
    
    message = db_helper.fetchone(sql, message_id)
    if not message:
        return show_reponse(code=Status.other, message="Message not found")
    
    id, name, msg_text, phone, attending, guests, created_at = message
    return show_reponse(
        data={
            "id": id,
            "name": name,
            "message": msg_text,
            "phone": phone,
            "attending": bool(attending),
            "guests": guests,
            "created_at": created_at.strftime("%Y-%m-%d %H:%M:%S")
        }
    )


@route("/api/wedding/save_message")
def save_wedding_message():
    """Save a new wedding message"""
    data = request.get("data")
    if not data:
        return show_reponse(code=Status.other, message="Missing parameters")
    
    name = data.get("name") or "匿名"
    message = data.get("message")
    
    # Validate required fields
    if not message:
        return show_reponse(code=Status.other, message="message are required")
    
    # Optional fields
    phone = data.get("phone", "")
    attending = data.get("attending", False)
    guests = data.get("guests", 0)
    
    # Current timestamp
    created_at = datetime.now()
    
    # Insert into database
    sql = """
    INSERT INTO wedding_messages (name, message, phone, attending, guests, created_at)
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    
    try:
        message_id = db_helper.execute_commit(
            sql, 
            (name, message, phone, attending, guests, created_at)
        )
        
        return show_reponse(
            data={
                "id": message_id,
                "name": name,
                "message": message,
                "phone": phone,
                "attending": attending,
                "guests": guests,
                "created_at": created_at.strftime("%Y-%m-%d %H:%M:%S")
            }
        )
    except Exception as e:
        logger.error(f"Failed to save wedding message: {e}")
        return show_reponse(code=Status.other, message="Failed to save message") 