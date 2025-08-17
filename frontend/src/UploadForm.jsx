import React, { useRef, useState } from "react";
import { uploadMedia } from "./api";

export default function UploadForm({ token, onUploaded }) {
  const fileInput = useRef();
  const [region, setRegion] = useState("NA");
  const [type] = useState("video");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async e => {
    e.preventDefault();
    setLoading(true);
    const file = fileInput.current.files[0];
    if (!file) return;
    const resp = await uploadMedia(file, region, type, token);
    setLoading(false);
    if (resp.id) {
      onUploaded(resp);
      alert("Upload successful!");
    } else {
      alert("Upload failed.");
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input type="file" ref={fileInput} accept=".mp4" required />
      <select value={region} onChange={e => setRegion(e.target.value)}>
        <option value="NA">North America</option>
        <option value="EU">Europe</option>
        <option value="APAC">Asia-Pacific</option>
      </select>
      <button type="submit" disabled={loading}>{loading ? "Uploading..." : "Upload"}</button>
    </form>
  );
}
