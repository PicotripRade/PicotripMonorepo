// packages/shared/src/api/getRequest.native.js
import { Platform } from "react-native";

const GetRequest = async (url) => {
  const response = await fetch(url, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
      // React Native doesn’t support cookies by default
      // Add Authorization header if needed
    },
  });

  if (!response.ok) {
    throw new Error(`Network error: ${response.status}`);
  }
  return response.json();
};

export default GetRequest;
