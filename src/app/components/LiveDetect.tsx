"use client";

import { use, useEffect, useRef, useState } from "react";
import { blob } from "stream/consumers";
export default function LiveDetect() {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  let baseUrl: string | undefined;
  baseUrl = "https://melmii2.vercel.app";
  if (process.env.NODE_ENV === "development") {
    baseUrl = process.env.NEXT_PUBLIC_API_URL;
  }

  const labelsRef = useRef<string[]>([]);
  const lastSummary = useRef<string>("");
  const isPlaying = useRef<boolean>(false);
  const [audioLocked, setAudioLocked] = useState(false);
  // const unlockedAudio = useRef<HTMLAudioElement | null>(null);
  const audioElRef = useRef<HTMLAudioElement | null>(null);
  const currentObjectURL = useRef<string | null>(null);

  const unlockAudio = () => {
    const audio = new Audio("outpuh.wav");
    audio
      .play()
      .then(() => {
        audio.pause();
        audioElRef.current = audio;
        setAudioLocked(true);
      })
      .catch((err) => {
        console.log("error:", err);
      });
  };

  useEffect(() => {
    if (!audioLocked) return;
    navigator.mediaDevices
      .getUserMedia({
        video: { facingMode: "environment" },
      })
      .then((stream) => {
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
        }
      });
    const interval = setInterval(async () => {
      try {
        await sigmer();
      } catch (e) {
        console.log(e);
        isPlaying.current = false;
      }
    }, 500);
    return () => clearInterval(interval);
  }, [audioLocked]);

  const playAudioBlob = (blob: Blob) => {
    const audioEl = audioElRef.current;
    if (!audioEl) {
      isPlaying.current = false;
      return;
    }
    if (currentObjectURL.current) {
      URL.revokeObjectURL(currentObjectURL.current);
    }
    const audioURL = URL.createObjectURL(blob);
    currentObjectURL.current = audioURL;
    audioEl.src = audioURL;
    audioEl.onended = () => {
      isPlaying.current = false;
    };
    audioEl.onerror = () => {
      isPlaying.current = false;
    };
    audioEl.play().catch((err) => {
      console.log("play() error:", err);
      isPlaying.current = false;
    });
  };

  const sigmer = async () => {
    console.log("Calling sigmer...");
    if (isPlaying.current) return;
    console.log("Passed isPlaying.current check...");
    isPlaying.current = true;
    const video = videoRef.current;
    const canvas = canvasRef.current;
    if (!video || !canvas) {
      isPlaying.current = false;
      return;
    }
    console.log("Passed !video || !canvas check...");
    console.log(
      `Video width: ${video.videoWidth}. Video height: ${video.videoHeight}`,
    );
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const context = canvas.getContext("2d");
    if (!context) {
      return;
    }
    console.log("Passed !context check...");
    context.drawImage(video, 0, 0, canvas.width, canvas.height); ///img, x, y, w, h
    canvas.toBlob(
      async (blob) => {
        if (!blob) {
          isPlaying.current = false;
          return;
        }
        console.log("Passed !blob check...");
        const formData = new FormData();
        formData.append("file", blob, "frammers.jpg"); //name blobvalue filename

        const responst = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL}/detect`,
          {
            method: "POST",
            // headers: {
            //   "Content-Type": "multipart/form-data",
            // },
            body: formData,
          },
        );
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
              console.log(det.class, det.confidence, det.bbox);
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
          console.log(summary);
          labelsRef.current.length = 0;
          // }
          if (summary && summary !== lastSummary.current) {
            lastSummary.current = summary;
            const re = await fetch(
              `${process.env.NEXT_PUBLIC_API_URL}/voice?words=${summary}`,
            );
            if (!re.ok) {
              isPlaying.current = false;
              return;
            }
            const audioBlob = await re.blob();
            playAudioBlob(audioBlob);
            return;
          }
        } else {
          console.log("failure");
        }
        isPlaying.current = false;
      },
      "image/jpeg",
      0.9,
    );
  };
  if (!audioLocked) {
    return (
      <div className="flex items-center justify-center h-screen">
        <button
          onClick={unlockAudio}
          className="text-sky-800 text-[15px] bg-white p-3 cursor-pointer rounded-lg font-bold"
        >
          Эхлэх
        </button>
      </div>
    );
  }

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
