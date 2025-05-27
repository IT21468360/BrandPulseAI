"use client";

/** 
 * Prevents any children from being rendered on the server so that
 * dangerouslySetInnerHTML (or other browser-only logic) only runs on the client.
 */
export default function ClientOnly({ children }) {
  return <>{children}</>;
}
