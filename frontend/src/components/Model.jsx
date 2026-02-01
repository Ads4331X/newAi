import React, { useEffect, useRef } from "react";
import * as PIXI from "pixi.js";
import { Live2DModel } from "pixi-live2d-display-lipsyncpatch";

window.PIXI = PIXI;

export function Model() {
  const containerRef = useRef(null);

  useEffect(() => {
  const app = new PIXI.Application({
  backgroundAlpha: 0,
  autoDensity: true,
  resolution: window.devicePixelRatio || 1,
  antialias: true,
  eventMode: "static",
});

app.ticker.maxFPS = 30;

    if (containerRef.current) {
      containerRef.current.appendChild(app.view);
    }

    const modelUrl = "/models/miku_pro_jp/runtime/miku_sample_t04.model3.json";

    Live2DModel.from(modelUrl)
      .then((model) => {
        app.stage.addChild(model);

        const desiredHeight = 450;
        const scale = desiredHeight / model.height;
        model.scale.set(scale);

        const mWidth = Math.round(model.width);
        const mHeight = Math.round(model.height);

        app.renderer.resize(mWidth, mHeight);

        model.anchor.set(0.65, 0.5);
        model.position.set(mWidth / 2, mHeight / 2);

        // IMPROVED interaction setup
        model.eventMode = "static"; // ADD THIS
        model.interactive = true;
        model.cursor = "pointer";

        model.on("pointerdown", (event) => {
          if (event.button === 0) {
            model.motion("Tap"); // left click
          } else if (event.button === 2) {
            const motion = ["FlickUp", "Flick"];
            const Random = Math.random();
            model.motion(Random > 0.5 ? motion[0] : motion[1]); // Right click
          }
        });

        // Prevent context menu on right click
        app.view.addEventListener("contextmenu", (e) => e.preventDefault());
        if (window.electronAPI) {
          window.electronAPI.resizeWindow(mWidth * 0.45, mHeight * 0.65);
        }
      })
      .catch((err) => {
        console.error("Error loading Live2D model:", err);
      });

    return () => {
      app.destroy(true, { children: true, texture: true });
    };
  }, []);

  return <div ref={containerRef} style={{ lineHeight: 0 }} />;
}
