import {MongoClient} from "mongodb";

const uri = process.env.MONGODB_URI; // Ensure this is in .env.local
let client;
let clientPromise;

console.log("Creating: " + uri);

if (!global._mongoClientPromise) {
  client = new MongoClient(uri);
  global._mongoClientPromise = client.connect();
}

clientPromise = global._mongoClientPromise;

export default clientPromise;
