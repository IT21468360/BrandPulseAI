import {createUser, getUserById, getAllUsers} from "@/models/userModel";
import bcrypt from "bcrypt";

// Hash password before saving
export async function createUserController(data) {
  const {name, email, username, password, role} = data;

  if (!name || !email || !username || !password || !role) {
    throw new Error("Missing required fields");
  }

  const hashedPassword = await bcrypt.hash(password, 10);

  return await createUser({
    name,
    email,
    username,
    password: hashedPassword,
    role,
  });
}

export async function getAllUsersController() {
  return await getAllUsers();
}

export async function getUserByIdController(id) {
  return await getUserById(id);
}
