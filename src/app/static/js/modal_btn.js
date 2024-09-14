export function handleModalClick() {
  const blueButton = document.querySelectorAll(".color-button.blue");
  blueButton.forEach(function (btn) {
    btn.onclick = function () {
      // Lấy phần tử cha gần nhất của nút này là '.grid-item' hoặc '.cluster-item'
      const item = btn.closest(".grid-item") || btn.closest(".cluster-item");
      // Tìm uri của ảnh trong item
      const imgURI = item.querySelector("img").src;
      // gọi BE để tìm videoURL và frameID từ imageURI
      $.ajax({
        url: "http://127.0.0.1:8000/find_prev_next_frame/",
        type: "POST",
        contentType: "application/json",
        data: JSON.stringify({
          url: imgURI,
        }),
        success: function (response) {
          console.log("Success:", response);
          if (response.prev) {
            console.log(response.prev);
            console.log(response.next);
            document.getElementById("imageModal").style.display = "block";
            document.getElementById("mainImage").src = imgURI;
            document.getElementById("frameImage1").src = response.prev;
            document.getElementById("frameImage2").src = response.next;
          } else {
            console.error("No data received from the server.");
          }
        },
        error: function (jqXHR, textStatus, errorThrown) {
          console.error("Error:", textStatus, errorThrown);
        },
      });
    };
  });

  const closeBlueButton = document.getElementById("close-modal-button");
  closeBlueButton.onclick = function () {
    document.getElementById("imageModal").style.display = "none";
  };
}
