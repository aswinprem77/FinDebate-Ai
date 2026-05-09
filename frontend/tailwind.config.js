/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#08111f",
        panel: "#111827",
        line: "#263241",
        cyan: "#20d4ff",
        mint: "#6ee7b7",
        amber: "#fbbf24"
      }
    }
  },
  plugins: []
};
