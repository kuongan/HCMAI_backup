export async function sendAudioToBackend(audioBlob) {
  try {
    const formData = new FormData();
    formData.append("audioFile", audioBlob, "recording.wav"); // Ensure the key is "audioFile"

    const response = await fetch("http://localhost:8000/speech_to_text", {
      method: "POST",
      body: formData,
    });
    const data = await response.json(); // Chuyển đổi dữ liệu thành JSON
    console.log("data: ",data); // Sử dụng dữ liệu
    return data;
    //   .then((response) => response.json())
    //   .then((data) => {
    //     console.log("Upload thành công:", typeof data);
    //     return data;
    //   })
    //   .catch((error) => {
    //     console.error("Error uploading file:", error);
    //   });
  } catch (error) {
    console.error("Error uploading file:", error);
  }
}
