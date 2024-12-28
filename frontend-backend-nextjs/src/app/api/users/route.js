import {
  createUserController,
  getAllUsersController,
} from "@/controllers/userController";

export async function GET(request) {
  try {
    const users = await getAllUsersController();
    return new Response(JSON.stringify(users), {
      status: 200,
      headers: {"Content-Type": "application/json"},
    });
  } catch (error) {
    return new Response(JSON.stringify({error: "Failed to fetch users"}), {
      status: 500,
      headers: {"Content-Type": "application/json"},
    });
  }
}

export async function POST(request) {
  try {
    const body = await request.json();
    const newUser = await createUserController(body);

    return new Response(JSON.stringify(newUser), {
      status: 201,
      headers: {"Content-Type": "application/json"},
    });
  } catch (error) {
    return new Response(
      JSON.stringify({error: error.message || "Failed to create user"}),
      {status: 400, headers: {"Content-Type": "application/json"}}
    );
  }
}
