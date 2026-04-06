export default async function saveFile(data){

    try{
        const handle = await saveFileWithPicker(data)
    }
    catch (err) {
        if (err.name === "AbortError"){
            return
        }
        else{
            saveFileFallback(data)
        }
    }

}

export async function saveFileWithPicker(data){

    try{

        const options = {
            suggestedName: "config.json",
            types: [
                {
                    description: ".json",
                    accept: {"application/json": [".json"]}
                }
            ]
        };
        
        const fileHandle = await window.showSaveFilePicker(options);

        const writableFileStream = await fileHandle.createWritable();

        await writableFileStream.write(
            new Blob([JSON.stringify(data, null, 2)], { type: "application/json" })
        )

        await writableFileStream.close();
    }

    catch (err) {
        console.error('Error saving config.json', err.name, err.message)
        throw err
    }

}

export async function saveFileFallback(data){
    const blob = new Blob([JSON.stringify(data, null, 2)])
    const a = document.createElement("a")
    a.href = URL.createObjectURL(blob)
    a.download = "config.json"
    a.click()
}