"use client";

import { use, useEffect, useRef, useState } from "react";
export default function LiveDetect() {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  let baseUrl = "https://melmii.vercel.app";
  if (process.env.NODE_ENV === "development") {
    baseUrl = "http://localhost:8000";
  }

  const labelsRef = useRef<string[]>([]);
  const lastSummary = useRef<string>("");
  const isPlaying = useRef(false);
  useEffect(() => {
    navigator.mediaDevices
      .getUserMedia({
        video: { facingMode: "environment" },
      })
      .then((stream) => {
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
        }
      });
    const interval = setInterval(() => {
      sigmer();
    }, 500);
    return () => clearInterval(interval);
  }, []);

  const sigmer = async () => {
    if (isPlaying.current) return;
    const video = videoRef.current;
    const canvas = canvasRef.current;
    if (!video || !canvas) {
      return;
    }
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const context = canvas.getContext("2d");
    context?.drawImage(video, 0, 0, canvas.width, canvas.height); ///img, x, y, w, h
    canvas.toBlob(
      async (blob) => {
        if (!blob) {
          return;
        }
        const formData = new FormData();
        formData.append("file", blob, "frammers.jpg"); //name blobvalue filename

        const responst = await fetch(`${baseUrl}/detect`, {
          method: "POST",
          // headers: {
          //   "Content-Type": "multipart/form-data",
          // },
          body: formData,
        });
        if (responst.ok) {
          const res = await responst.json();
          let dets: {
            class: string;
            confidence: number;
            bbox: [number, number, number, number];
          }[] = res.detections;
          // const newContext = canvas.getContext("2d");
          // newContext?.drawImage(video, 0, 0, canvas.width, canvas.height);
          dets.forEach((det) => {
            // if (det.confidence >= 0.6 && newContext) {
            if (det.confidence >= 0.6 && labelsRef.current) {
              // console.log(det.class, det.confidence, det.bbox);
              labelsRef.current.push(det.class);
              //     const [x1, y1, x2, y2] = element.bbox;
              //     const w = x2 - x1;
              //     const h = y2 - y1;
              //     newContext.strokeStyle = "red";
              //     newContext.strokeRect(x1, y1, w, h);
              //     newContext.fillStyle = "red";
              //     newContext.font = "bold 20px sans-serif";
              //     newContext.fillText(element.class, x1, y1);
            }
          });
          // if (labelsRef.current) {
          const counts = labelsRef.current.reduce<Record<string, number>>(
            (accum, label) => {
              accum[label] = (accum[label] || 0) + 1;
              return accum;
            },
            {},
          );

          const summary = Object.entries(counts)
            .map(([name, count]) => `${count} ${name}`)
            .join(" ");
          // console.log(summary);
          labelsRef.current.length = 0;
          // }
          if (summary && summary !== lastSummary.current) {
            const re = await fetch(`${baseUrl}/voice?words=${summary}`);
            if (!re.ok) {
              const err = await re.text();
              // console.log(err);
              isPlaying.current = false;
              return;
            }
            isPlaying.current = true;
            const blob = await re.blob();
            const audioURL = URL.createObjectURL(blob);
            const audio = new Audio(audioURL);
            audio.addEventListener("ended", () => {
              URL.revokeObjectURL(audioURL);
              isPlaying.current = false;
            });
            audio.play();
            lastSummary.current = summary;
          }
        } else {
          console.log("failure");
        }
      },
      "image/jpeg",
      0.9,
    );
  };

  return (
    // <div className="relative">
    //   <video ref={videoRef} autoPlay playsInline muted />
    //   <canvas ref={canvasRef} className="absolute top-0 left-0" />
    // </div>
    <div>
      <video ref={videoRef} autoPlay playsInline muted />
      <canvas ref={canvasRef} className="hidden" />
    </div>
  );
}
