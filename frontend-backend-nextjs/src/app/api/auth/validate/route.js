import {NextResponse} from "next/server";
import jwt from "jsonwebtoken";

const JWT_SECRET = process.env.JWT_SECRET; // Ensure this is set in your .env.local file

export async function POST(request) {
  try {
    const authHeader = request.headers.get("Authorization");

    if (!authHeader || !authHeader.startsWith("Bearer ")) {
      return NextResponse.json(
        {error: "Authorization token is missing or invalid"},
        {status: 401}
      );
    }

    const token = authHeader.split(" ")[1];

    // Verify the token
    const decoded = jwt.verify(token, JWT_SECRET);

    // Return success if the token is valid
    return NextResponse.json(
      {message: "Token is valid", user: decoded},
      {status: 200}
    );
  } catch (error) {
    // Handle errors such as token expiration or invalid signature
    return NextResponse.json(
      {error: "Invalid or expired token"},
      {status: 401}
    );
  }
}
