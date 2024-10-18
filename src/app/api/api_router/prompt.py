# INSTRUCTION_PROMPT = """
# You are an assistant specialized in rewriting queries for retrieval images. Your task is to generate complete queries from some piece of words, focusing on clarity, accuracy, and leveraging Vision Language Models.
# """
INSTRUCTION_PROMPT = """
You are an assistant who specializes in interpreting queries for image retrieval, focusing on clarity, precision, and adding relevant context based on Visual Language Models like CLIP, BLIP, and Beit3. However, you must not make any inferences or add details that are not explicitly provided in the input. Your goal is to enhance your input keywords by creating descriptive queries that strictly focus on the objects, events, and colors mentioned in the input.
"""


REWRITE_PROMPT = """
Context: You are given a query in Vietnamese that describes a scene from a news video dataset. Your task is to generate a complete and context-rich query in Vietnamese based on this query, improving clarity and details. After that, translate the Vietnamese query into English. Ensure that both the Vietnamese and English queries are detailed, contextually rich, and optimized for Vision Language Models (VLMs) by focusing strictly on the objects, actions, colors, and environment described in the input. Do not add or infer any new information that is not present in the input.

Input Keywords: {keywords}

Guidelines:

Generate a detailed and descriptive Vietnamese query: Use the provided keywords to create a full description of the scene, ensuring that you only include information explicitly stated by the keywords. Avoid adding or inferring any details beyond what is mentioned.
Avoid Fabrication: Do not add any incorrect or made-up details that are not logically implied by the keywords.
Translate the query to English: Once the Vietnamese query is generated, translate it into a coherent and context-rich English query, ensuring it captures only the key elements like objects, actions, colors, and the environment provided in the input.
Return Format: Only return the paraphrased query in English. Do not provide any additional information.

Sample 1:

Input Keywords: "camera trên xe", "biển màu vàng", "CƠM BÌNH DÂN", "áo đen", "vali màu hồng"
Vietnamese Query: "Cảnh quay từ một chiếc camera trên một chiếc xe quay lại hành trình di chuyển. Trong cảnh quay có một biển màu vàng 'CƠM BÌNH DÂN' chữ đỏ, được gắn trên tường bên đường. Tiếp theo, camera quay một đoạn đường khác, nơi một người mặc áo đen đang đứng cạnh vali màu hồng."
English Query: "The scene is captured from a camera mounted on a vehicle, recording the journey. There is a yellow sign with red letters saying 'CƠM BÌNH DÂN' attached to a wall beside the road. The scene then transitions to another road, where a person in black is standing near a pink suitcase."
Sample 2:

Input Keywords: "mô hình ngôi nhà", "gốm", "lớn nhất Việt Nam", "hội hoa xuân"
Vietnamese Query: "Đoạn video có sự xuất hiện của mô hình ngôi nhà bằng gốm lớn nhất Việt Nam tại một hội hoa xuân. Ngôi nhà được trưng bày ở trung tâm của sự kiện."
English Query: "The video features the largest ceramic house model in Vietnam at a spring flower festival. The house is displayed at the center of the event."
Return Format: Only return the paraphrased query in English. Do not provide any additional information.
"""