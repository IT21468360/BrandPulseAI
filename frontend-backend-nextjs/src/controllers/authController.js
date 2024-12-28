import {getUserByEmail} from "@/models/userModel";
import bcrypt from "bcrypt";
import jwt from "jsonwebtoken";

export async function signInController(email, password) {
  // Validate input
  if (!email || !password) {
    throw new Error("Email and password are required.");
  }

  // Fetch user from the database
  const user = await getUserByEmail(email);
  if (!user) {
    throw new Error("Invalid email or password.");
  }

  // Compare password
  const isPasswordValid = await bcrypt.compare(password, user.password);
  if (!isPasswordValid) {
    throw new Error("Invalid email or password.");
  }

  // Generate JWT token
  const token = jwt.sign(
    {id: user._id, email: user.email, role: user.role}, // Payload
    process.env.JWT_SECRET, // Secret key
    {expiresIn: process.env.JWT_EXPIRY} // Options
  );

  // Return token and user data
  return {
    token,
    user: {
      id: user._id,
      name: user.name,
      email: user.email,
      username: user.username,
      role: user.role,
    },
  };
}
