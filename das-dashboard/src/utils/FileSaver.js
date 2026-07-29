export async function saveFileWithPicker(data) {
  const payload = typeof data === "string" ? data : JSON.stringify(data, null, 2)

  try {
    const options = {
      suggestedName: "config.json",
      types: [
        {
          description: ".json",
          accept: { "application/json": [".json"] }
        }
      ]
    }

    const fileHandle = await window.showSaveFilePicker(options)
    const writableFileStream = await fileHandle.createWritable()

    await writableFileStream.write(
      new Blob([payload], { type: "application/json" })
    )

    await writableFileStream.close()
  } catch (err) {
    console.error("Error saving config.json", err.name, err.message)
    throw err
  }
}

export default async function saveFile(data) {
  try {
    await saveFileWithPicker(data)
  } catch (err) {
    if (err.name === "AbortError") {
      return
    }
    saveFileFallback(data)
  }
}

export async function saveFileFallback(data) {
  const payload = typeof data === "string" ? data : JSON.stringify(data, null, 2)
  const blob = new Blob([payload], { type: "application/json" })
  const a = document.createElement("a")
  a.href = URL.createObjectURL(blob)
  a.download = "config.json"
  a.click()
}
