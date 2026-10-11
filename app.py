import streamlit as st
from PIL import Image
import requests
import base64
from io import BytesIO

# --- Cấu hình giao diện Streamlit ---
st.set_page_config(
    page_title="Ứng dụng AI Nhận diện Bệnh Lá Cà Phê", 
    page_icon="☕", 
    layout="centered"
)

# --- THÔNG TIN CẤU HÌNH ROBOFLOW ---
ROBOFLOW_API_KEY = "VJBE8s72PByt8YgppZzb" 
# Model ID cho Version 2 của bạn trên Roboflow
#MODEL_ID = "caphe/4"  
MODEL_ID = "phuoc-quy-nguyen-s-workspace/caphe-7-resnet18-t1"
# --- Cơ sở dữ liệu kiến thức về bệnh hại cây cà phê ---
disease_database = {
    'Coffee_Leaf_Rust': {
        'display_name': 'Bệnh Gỉ sắt (Coffee Leaf Rust)',
        'description': """**Tác nhân:** Do nấm *Hemileia vastatrix* gây ra.\n**Triệu chứng:** Mặt dưới lá xuất hiện các đốm tròn nhỏ màu vàng nhạt, phủ bột màu cam sậm.""",
        'solution': """* **🌿 Cắt tỉa:** Tạo độ thông thoáng cho tán cây.\n* **💊 Thuốc bảo vệ:** Phun các thuốc gốc Đồng hoặc hoạt chất Hexaconazole khi bệnh mới chớm.""",
        'prevention': "Sử dụng các giống cà phê kháng gỉ sắt."
    },
    'Brown_Eye_Spot': {
        'display_name': 'Bệnh Đốm mắt cua (Cercospora)',
        'description': """**Tác nhân:** Do nấm *Cercospora coffeicola* gây ra.\n**Triệu chứng:** Vết bệnh hình tròn, tâm màu xám trắng, viền ngoài màu nâu sẫm nhìn rất giống mắt cua.""",
        'solution': """* **🌿 Canh tác:** Đắp thêm phân hữu cơ, bổ sung đầy đủ phân đạm.\n* **💊 Thuốc bảo vệ:** Phun phòng hoặc trị bằng các thuốc chứa hoạt chất Carbendazim.""",
        'prevention': "Quản lý dinh dưỡng cây trồng thật tốt ngay từ đầu mùa mưa."
    },
    'Anthracnose_Leaf': {
        'display_name': 'Bệnh Thán thư hại lá (Anthracnose)',
        'description': """**Tác nhân:** Do nấm *Colletotrichum coffeanum* gây ra.\n**Triệu chứng:** Trên lá tạo thành các đốm nâu vòng đồng tâm lan từ mép lá vào.""",
        'solution': """* **🌿 Hành động:** Bẻ bỏ các cành khô, cành chết.\n* **💊 Thuốc bảo vệ:** Sử dụng các thuốc có chứa hoạt chất Tebeconazole, Mancozeb.""",
        'prevention': "Bón bổ sung các chế phẩm nấm đối kháng Trichoderma vào đất."
    },
    'Red_Alga': {
        'display_name': 'Bệnh Đốm tảo đỏ (Red Alga)',
        'description': """**Tác nhân:** Do loài tảo *Cephaleuros virescens* gây ra.\n**Triệu chứng:** Mặt trên của lá xuất hiện các đốm tròn màu cam, hơi nổi lên như nhung.""",
        'solution': """* **🌿 Hành động:** Rong tỉa cành vô hiệu, dọn sạch cỏ dại.\n* **💊 Thuốc bảo vệ:** Sử dụng các loại thuốc gốc đồng như COC 85 để phun phủ đều.""",
        'prevention': "Tỉa cành tạo tán định kỳ hàng năm."
    },
    'healthy': {
        'display_name': 'Lá Cà Phê Khỏe mạnh (Healthy)',
        'description': "### 🎉 Chúc mừng! Cây cà phê của bạn đang rất khỏe mạnh.\nLá cây xanh bóng mượt, phiến lá dày, không có đốm nấm.",
        'solution': """* **💧 Tưới nước:** Đảm bảo tưới đủ nước giai đoạn siết nước làm bông.\n* **🧪 Dinh dưỡng:** Bón phân NPK cân đối theo từng chu kỳ.""",
        'prevention': "Thường xuyên kiểm tra các nách lá để phát hiện sớm rệp sáp."
    }
}

def du_doan_benh_chuan(anh_pil):
    """Gửi ảnh dạng mã hóa Base64 trực tiếp lên Server Classification của Roboflow"""
    try:
        buffered = BytesIO()
        anh_pil.save(buffered, format="JPEG", quality=95)
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        
        # Endpoint chuyên dụng cho mô hình Phân loại (Classification API)
        url = f"https://classify.roboflow.com/{MODEL_ID}?api_key={ROBOFLOW_API_KEY}"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        
        response = requests.post(url, data=img_str, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": {"message": f"Lỗi HTTP {response.status_code}: {response.text}"}}
    except Exception as e:
        return {"error": {"message": str(e)}}

# --- Thiết kế Giao diện UI ---
st.markdown("""
<style>
    .stApp { background-color: #fcfaf7; }
    h1 { color: #4E342E; text-align: center; font-weight: bold; margin-bottom: 25px; }
    .footer { text-align: center; margin-top: 50px; color: #777; font-size: 0.9em; border-top: 1px solid #ddd; padding-top: 15px; }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1>☕ ỨNG DỤNG AI NHẬN DIỆN BỆNH QUA LÁ CÀ PHÊ 🍃</h1>", unsafe_allow_html=True)

tep_anh = st.file_uploader(label="Tải ảnh lá cà phê lên hệ thống", type=["jpg", "jpeg", "png"])

if tep_anh is not None:
    anh = Image.open(tep_anh).convert("RGB")
    st.image(anh, caption="📷 Ảnh lá cà phê bạn đã tải lên", use_container_width=True)
    
    with st.spinner("🔍 Hệ thống AI đang phân tích dữ liệu phiến lá... Vui lòng chờ ⏳"):
        try:
            ket_qua = du_doan_benh_chuan(anh)
            
            if "error" in ket_qua:
                st.error("❌ Hệ thống phản hồi lỗi kết nối mạng hoặc sai MODEL_ID:")
                st.warning(ket_qua["error"].get("message"))
            else:
                ten_benh_goc = None
                do_tin_cay = 0.0
                
                # Bóc tách kết quả từ Classification API
                if "top" in ket_qua:
                    ten_benh_goc = ket_qua["top"]
                    do_tin_cay = ket_qua.get("confidence", 0.0)
                elif "predictions" in ket_qua:
                    predictions = ket_qua["predictions"]
                    if isinstance(predictions, dict):
                        ten_benh_goc = max(predictions, key=lambda k: predictions[k].get("confidence", 0) if isinstance(predictions[k], dict) else predictions[k])
                        if isinstance(predictions[ten_benh_goc], dict):
                            do_tin_cay = predictions[ten_benh_goc].get("confidence", 0.0)
                        else:
                            do_tin_cay = predictions[ten_benh_goc]

                if do_tin_cay <= 1.0:
                    do_tin_cay *= 100

                if ten_benh_goc:
                    info = disease_database.get(ten_benh_goc)
                    if info:
                        st.success(f"**Kết quả phân tích:** {info['display_name']} *(Độ tin cậy: {do_tin_cay:.1f}%)*")
                        with st.expander("📝 Xem chi tiết triệu chứng bệnh"):
                            st.markdown(info['description'])
                        with st.expander("✅ Hướng dẫn xử lý và chữa trị"):
                            st.markdown(info['solution'])
                    else:
                        ten_chuan_hoa = ten_benh_goc.replace('_', ' ').title()
                        st.warning(f"**AI nhận diện được nhãn:** `{ten_chuan_hoa}` *(Độ tin cậy: {do_tin_cay:.1f}%)*")
                        st.error(f"⚠️ Nhãn bệnh `{ten_benh_goc}` từ mô hình chưa có trong từ điển `disease_database`.")
                else:
                    st.info("Cấu trúc dữ liệu trả về từ Roboflow:")
                    st.json(ket_qua)
                
        except Exception as e:
            st.error(f"❌ Đã xảy ra lỗi hệ thống nội bộ: {e}")

st.markdown("<div class='footer'>Hệ thống thử nghiệm Nghiên cứu khoa học - Phát triển bởi Nhóm Nghiên cứu AI trường THPT Hoàng Hoa Thám</div>", unsafe_allow_html=True)
