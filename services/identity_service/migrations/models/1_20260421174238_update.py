from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "schools" (
    "id" UUID NOT NULL PRIMARY KEY,
    "name" VARCHAR(255) NOT NULL UNIQUE,
    "address" VARCHAR(255),
    "contact_email" VARCHAR(255)
);
        ALTER TABLE "users" ADD "school_id" UUID;
        ALTER TABLE "users" ADD CONSTRAINT "fk_users_schools_c7608427" FOREIGN KEY ("school_id") REFERENCES "schools" ("id") ON DELETE CASCADE;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "users" DROP CONSTRAINT IF EXISTS "fk_users_schools_c7608427";
        ALTER TABLE "users" DROP COLUMN "school_id";
        DROP TABLE IF EXISTS "schools";"""
