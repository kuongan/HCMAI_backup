// Hàm để cập nhật thông tin frame_ID và video_ID từ src của mainImage
function updateImageInfo() {
  // Lấy src của hình chính
  const imgURI = document.getElementById("mainImage").src;

  // Tách frame_ID và video_ID từ URI
  const uriParts = imgURI.split('/');
  const imageName = uriParts[uriParts.length - 1];
  const [frameID] = imageName.split('_').slice(0, 1);
  const videoID = uriParts[6];

  // Cập nhật thông tin lên phần tử #image-info
  document.getElementById("image-info").innerText = `Frame ID: ${frameID}, Video ID: ${videoID}`;
}

export function handleModalClick() {
  const blueButton = document.querySelectorAll(".color-button.blue");
  blueButton.forEach(function (btn) {
    btn.onclick = function () {
      const item = btn.closest(".grid-item") || btn.closest(".cluster-item");
      const imgURI = item.querySelector("img").src;

      $.ajax({
        url: "http://127.0.0.1:8000/find_prev_next_frame/",
        type: "POST",
        contentType: "application/json",
        data: JSON.stringify({ url: imgURI }),
        success: function (response) {
          console.log("Success:", response);
          if (response.prev) {
            updateImageInfo(); 
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

  // Đóng modal khi nhấn nút đóng
  const closeBlueButton = document.getElementById("close-modal-button");
  closeBlueButton.onclick = function () {
    document.getElementById("imageModal").style.display = "none";
  };

  // Đóng modal khi bấm ra ngoài nội dung modal
  const modal = document.getElementById("imageModal");
  modal.onclick = function (event) {
    // Kiểm tra nếu click nằm ngoài phần tử .modal-content
    if (event.target === modal) {
      modal.style.display = "none";
    }
  };

  // Sự kiện click cho hai ảnh nhỏ
  const frameImages = document.querySelectorAll(".small-frame-image");
  frameImages.forEach(function (img) {
    img.onclick = function () {
      const currentSrc = img.src;
      document.getElementById("mainImage").src = currentSrc;

      $.ajax({
        url: "http://127.0.0.1:8000/find_prev_next_frame/",
        type: "POST",
        contentType: "application/json",
        data: JSON.stringify({ url: currentSrc }),
        success: function (response) {
          console.log("Success:", response);
          if (response.prev && response.next) {
            updateImageInfo(); 
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
}
