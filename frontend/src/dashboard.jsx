import React, { useEffect, useState } from "react";
import { fetchDashboard } from "./api";

export default function Dashboard({ token, region }) {
  const [logs, setLogs] = useState({});

  useEffect(() => {
    fetchDashboard(token, region).then(setLogs);
  }, [token, region]);

  return (
    <div>
      <h2>Detection Logs by Region</h2>
      {Object.entries(logs).map(([region, detections]) => (
        <div key={region}>
          <h3>{region}</h3>
          <ul>
            {detections.map((det, i) => (
              <li key={i}>
                {det.timestamp}: {det.filename} → {det.classification} ({det.confidence})
              </li>
            ))}
          </ul>
        </div>
      ))}
    </div>
  );
}
