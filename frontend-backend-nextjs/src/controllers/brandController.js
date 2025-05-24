import { createBrand, getBrandsByUserId } from "@/models/brandModel";
import clientPromise from "@/db/mongodb/client";

// ✅ Register a New Brand (Supports multiple URLs)
export const registerBrand = async ({ user_id, brand_name, industry, websites, address, phone }) => {
  try {
    if (!user_id || !brand_name || !industry || !websites || websites.length === 0 || !address || !phone) {
      return { success: false, message: "All fields are required including at least one website." };
    }

    const client = await clientPromise;
    const db = client.db(process.env.DB_NAME);

    // Check if brand already exists
    const existingBrand = await db.collection("brands").findOne({ user_id, brand_name });

    if (existingBrand) {
      return { success: false, message: "Brand already exists!" };
    }

    // Save new brand
    const newBrand = await createBrand({ user_id, brand_name, industry, websites, address, phone });

    return { success: true, message: "Brand registered successfully!", brand: newBrand };
  } catch (error) {
    console.error("❌ Error in registerBrand:", error);
    return { success: false, message: "Server error", error: error.message };
  }
};

// ✅ Get Brands by User (Return websites array for dropdown)
export const getUserBrands = async (user_id) => {
  try {
    if (!user_id) {
      return { success: false, message: "User ID is required." };
    }

    const client = await clientPromise;
    const db = client.db(process.env.DB_NAME);

    const brands = await db.collection("brands")
      .find({ user_id })
      .project({ brand_name: 1, websites: 1}) 
      .toArray();

    return { success: true, brands };
  } catch (error) {
    console.error("❌ Error fetching brands:", error);
    return { success: false, message: "Server error", error: error.message };
  }
};
