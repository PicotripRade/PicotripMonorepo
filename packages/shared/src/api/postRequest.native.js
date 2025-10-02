// packages/shared/src/api/postRequest.native.js
const PostRequest = async (url, data) => {
  const response = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    throw new Error(`Network error: ${response.status}`);
  }
  return response.json();
};

export default PostRequest;
