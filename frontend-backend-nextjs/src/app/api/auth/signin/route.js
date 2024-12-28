import {signInController} from "@/controllers/authController";

export async function POST(request) {
  try {
    const {email, password} = await request.json();

    // Call the Sign-In Controller
    const response = await signInController(email, password);

    // Return the token and user data
    return new Response(JSON.stringify(response), {
      status: 200,
      headers: {"Content-Type": "application/json"},
    });
  } catch (error) {
    return new Response(
      JSON.stringify({error: error.message || "Failed to sign in"}),
      {status: 400, headers: {"Content-Type": "application/json"}}
    );
  }
}
