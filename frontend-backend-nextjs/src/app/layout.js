import "./styles/globals.css";
import {ThemeProvider} from "./context/ThemeContext";
import {AuthProvider} from "./context/AuthContext";
import ThemeToggle from "./components/ThemeToggle";

export default function RootLayout({children}) {
  return (
    <html lang="en">
      <head>
        <meta charSet="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>Your App</title>
      </head>
      <body>
        {/* Wrap your app with the ThemeProvider */}
        <AuthProvider>
          <ThemeProvider>
            <ThemeToggle />
            {children}
          </ThemeProvider>
        </AuthProvider>
      </body>
    </html>
  );
}
