import config from "./config";

export async function uploadMedia(file, region, type, token) {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("region", region);
  formData.append("type", type);

  const res = await fetch(`${config.API_BASE_URL}/media/upload`, {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${token}`,
      "X-Region-ID": region
    },
    body: formData
  });
  return await res.json();
}

export async function fetchDashboard(token, region) {
  const res = await fetch(`${config.API_BASE_URL}/detection/dashboard`, {
    headers: {
      "Authorization": `Bearer ${token}`,
      "X-Region-ID": region
    }
  });
  return await res.json();
}
