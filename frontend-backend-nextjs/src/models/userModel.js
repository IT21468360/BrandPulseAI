import {z} from "zod";
import clientPromise from "@/db/mongodb/client";

// MongoDB Database Name
const db_name = process.env.DB_NAME;
const COLLECTION_NAME = "users";

// Define the User Schema
const UserSchema = z.object({
  name: z.string().min(1, "Name is required"),
  email: z.string().email("Invalid email format"),
  username: z.string().min(3, "Username must be at least 3 characters long"),
  password: z.string().min(6, "Password must be at least 6 characters long"),
  role: z.enum(["admin", "user", "manager"]), // Predefined roles
});

// Validate Data Against the Schema
export function validateUser(data) {
  return UserSchema.parse(data); // Throws an error if invalid
}

// Database Operations
export async function createUser(user) {
  const client = await clientPromise;
  const db = client.db(db_name);

  // Check if the email already exists
  const existingUser = await db
    .collection(COLLECTION_NAME)
    .findOne({email: user.email});
  if (existingUser) {
    throw new Error("A user with this email already exists.");
  }

  // Insert the user into the database
  const result = await db.collection(COLLECTION_NAME).insertOne(user);
  // Return the newly created user document or its ID
  return {
    // id: result.insertedId,
    ...user,
  };
}

export async function getUserById(id) {
  const client = await clientPromise;
  const db = client.db(db_name);
  return await db.collection(COLLECTION_NAME).findOne({_id: id});
}

export async function getUserByEmail(email) {
  const client = await clientPromise;
  const db = client.db(db_name);

  // Find user by email
  return await db.collection(COLLECTION_NAME).findOne({email});
}

export async function getAllUsers() {
  const client = await clientPromise;
  const db = client.db(db_name);
  return await db.collection(COLLECTION_NAME).find({}).toArray();
}
