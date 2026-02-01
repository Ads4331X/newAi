import { Model } from "./components/Model";

function App() {
  return (
    <div>
      {/* Only this part is draggable */}
      <div style={{ WebkitAppRegion: "drag", height: "30px" }}>Drag here</div>

      {/* Model is NOT draggable, so clicks work */}
      <div style={{ WebkitAppRegion: "no-drag" }}>
        <Model />
      </div>
    </div>
  );
}

export default App;
