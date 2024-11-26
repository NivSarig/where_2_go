export const BACKEND =
  process.env.NODE_ENV === "production"
    ? "http://route-your-way.ops-optibus.com:8000"
    : "http://localhost:8000";
