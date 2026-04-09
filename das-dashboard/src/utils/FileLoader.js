export default function handleLoadConfig(event, onLoad) {
  const file = event.target.files[0];
  if (!file) return;

  const reader = new FileReader();

  reader.onload = (e) => {
    try {
      const parsed = JSON.parse(e.target.result);

      onLoad(parsed);
    } 
    catch (err) {
      console.error("Invalid JSON:", err);
      alert("Invalid JSON file");
    }
  };

  reader.readAsText(file);
};