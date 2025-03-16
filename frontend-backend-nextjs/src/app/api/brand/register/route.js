import { NextResponse } from "next/server";
import { registerBrand } from "@/controllers/brandController";

export async function POST(req) {
  try {
    console.log("🟢 POST request received at /api/brand/register");

    const body = await req.json();
    console.log("🟢 Received request body:", body);

    if (!body.user_id) {
      console.error("❌ Missing user_id in request!");
      return NextResponse.json({ message: "User ID is missing. Please log in again." }, { status: 400 });
    }

    const response = await registerBrand(body);
    console.log("🟢 registerBrand() Response:", response);

    if (!response.success) {
      return NextResponse.json({ message: response.message }, { status: 400 });
    }

    return NextResponse.json({ message: response.message, brand: response.brand }, { status: 201 });
  } catch (error) {
    console.error("❌ Server error in POST /api/brand/register:", error);
    return NextResponse.json({ message: "Server error", error: error.message }, { status: 500 });
  }
}
