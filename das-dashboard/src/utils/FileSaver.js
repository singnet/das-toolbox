export default async function saveFileWithPicker(data){

    try{

        const options = {
            suggestedName: "config.json",
            types: [
                {
                    description: "Json configuration for DAS/DAS-CLI",
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
    }

}