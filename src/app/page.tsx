"use client";
import Image from "next/image";
import { useRef, useState } from "react";
import LiveDetection from "./components/LiveDetect";
import { Bayon } from "next/font/google";

const bayon = Bayon({
  weight: "400",
  subsets: ["latin"],
});

export default function Home() {
  return (
    <div className="workpls flex flex-col flex-1 items-center justify-center bg-zinc-50 font-sans">
      <header className="bg-sky-500 w-full relative flex h-15 items-center justify-between px-5 nowwork">
        <div className="flex">
          <Image src="Union.svg" alt="Melmii Logo" width={50} height={50} />
          <Image
            src="MELMII.svg"
            alt="Logo"
            width={70}
            height={70}
            className="ml-4"
          />
        </div>
        <div className="text-sky-800 text-[15px] bg-white p-2 rounded-lg font-bold">
          <a href="#about">Бидний Тухай</a>
        </div>
      </header>
      <section className="bg-[#A1A1AA] w-full overflow-hidden">
        <LiveDetection />
      </section>
      <main
        className="w-full bg-[url(eyes.svg)] bg-size-[70px] flex flex-wrap justify-around py-20 pleasee"
        id="about"
      >
        <div className="flex flex-col justify-center">
          <Image src="/hero.png" alt="mascot" width={700} height={700} />
        </div>
        <div className="flex flex-col justify-center max-w-150">
          <h1 className={`text-[60px] text-white font-bold`}>
            МЭЛМИЙД ТАВТАЙ МОРИЛ
          </h1>
          <div className="text-xl text-white">
            Харааны бэрхшээлтэй хүмүүст зориулан бүтээгдсэн аливаа эд зүйлсийг
            мэдрэн таньж Монгол хэлээр хэлдэг вэб апп.
          </div>
        </div>
      </main>
      <footer className="w-full p-10 bg-size-[70px] flex justify-center align-center">
        <div className="font-bold text-zinc-400">©Oculus Reparo</div>
      </footer>
    </div>
  );
}
// export default async function MyNextFastAPIApp() {
//   const role = await fetchEngineerRole();

//   return (
//     <>
//       <div>{`The main skill of a ${role.title} is ${role.mainskill}.`}</div>
//     </>
//   );
// }

// async function fetchEngineerRole() {
//   let baseUrl = "http://localhost:3000";
//   const title = "Frontend Developer";
//   try {
//     const response = await fetch(
//       `${baseUrl}/api/py/engineer-roles?title=${title}`,
//     );
//     if (!response.ok) {
//       throw new Error("Failed to fetch data");
//     }
//     const role = await response.json();
//     return role;
//   } catch (error) {
//     console.error("Error fetching engineer role:", error);
//     return null;
//   }
// }
