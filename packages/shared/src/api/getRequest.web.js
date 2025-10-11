// packages/shared/src/api/getRequest.web.js
const GetRequest = async (url) => {
  const response = await fetch(url, {
    method: "GET",
    credentials: "include", // keep cookies for web
    headers: {
      "Content-Type": "application/json",
    },
  });

  if (!response.ok) {
    throw new Error(`Network error: ${response.status}`);
  }
  return response.json();
};

export default GetRequest;
