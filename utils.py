import aiosqlite
from google import generativeai as genai

class MessageDB:
    def __init__(self, path: str) -> None:
        self.path = path
    
    async def create_tables(self) -> None:
        async with aiosqlite.connect(self.path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS content(
                        id INTEGER PRIMARY KEY,
                        owner_id TEXT NOT NULL,
                        role TEXT NOT NULL
                    )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS part(
                        id INTEGER PRIMARY KEY,
                        content_id INTEGER,
                        is_text BOOLEAN NOT NULL,
                        text TEXT,
                        mime_type TEXT,
                        data BLOB,
                        FOREIGN KEY (content_id) REFERENCES content (id) ON DELETE CASCADE ON UPDATE CASCADE
                    )
            """)
    
    async def insert_history(self, owner_id: str, history: list[genai.protos.Content]) -> None:
        async with aiosqlite.connect(self.path) as db:
            for msg in history:
                # Insert initial message
                query = "INSERT INTO content(owner_id, role) VALUES(?, ?)"
                async with db.execute(query, (owner_id, msg.role)) as cur:
                    content_id = cur.lastrowid

                # Insert all parts of message
                for part in msg.parts:
                    if part.text:
                        await db.execute("""
                            INSERT INTO part(content_id, is_text, text) VALUES(?, ?, ?)
                        """, (content_id, True, part.text))
                    elif part.inline_data:
                        await db.execute("""
                            INSERT INTO part(content_id, is_text, mime_type, data) VALUES(?, ?, ?, ?)
                        """, (content_id, False, part.inline_data.mime_type, part.inline_data.data))
            await db.commit()
    
    async def get_history(self, owner_id: str) -> list[genai.protos.Content]:
        history = []
        async with aiosqlite.connect(self.path) as db:
            query = """
                WITH content_owner AS (
                    SELECT id, role
                    FROM content
                    WHERE owner_id=?
                    ORDER by id ASC
                )
                SELECT c.id, c.role, p.is_text, p.text, p.mime_type, p.data
                FROM content_owner c
                JOIN part p ON c.id=p.content_id
            """
            last_id = -1
            async with db.execute(query, (owner_id,)) as cur:
                async for row in cur:
                    content_id, role, is_text, text, mime_type, data = row

                    if content_id != last_id:
                        parts = []

                    if is_text:
                        parts.append(genai.protos.Part(text=text))
                    else:
                        parts.append(genai.protos.Part(
                            inline_data=genai.protos.Blob(
                                mime_type=mime_type,
                                data=data
                            )
                        ))
                    
                    history.append(
                        genai.protos.Content(
                            role=role,
                            parts=parts
                        )
                    )
        return history