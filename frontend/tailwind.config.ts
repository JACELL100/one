import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        // one8 performance identity — deep ink base + electric accent.
        ink: {
          950: "#05060a",
          900: "#0a0c14",
          800: "#12151f",
          700: "#1b1f2b",
        },
        volt: {
          400: "#c7ff3e",
          500: "#a8f000",
          600: "#8fd000",
        },
        ember: {
          500: "#ff5a3c",
        },
      },
      fontFamily: {
        display: ["var(--font-display)", "system-ui", "sans-serif"],
        sans: ["var(--font-sans)", "system-ui", "sans-serif"],
      },
      backgroundImage: {
        "grid-fade":
          "radial-gradient(circle at 50% 0%, rgba(168,240,0,0.10), transparent 60%)",
      },
    },
  },
  plugins: [],
};

export default config;
