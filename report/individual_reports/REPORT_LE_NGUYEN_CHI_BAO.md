# Individual Report: Lab 3 - Chatbot vs ReAct Agent

- **Student Name**: Le Nguyen Chi Bao
- **Student ID**: 2A202600103
- **Date**: 2025-05-05

---

## I. Technical Contribution (15 Points)

*Describe your specific contribution to the codebase (e.g., implemented a specific tool, fixed the parser, etc.).*

- **Modules Implementated**: [e.g., `src/tools/search_tool.py`]
- **Code Highlights**: [Copy snippets or link file lines]
- **Documentation**: [Brief explanation of how your code interacts with the ReAct loop]
Modules Implementated: search_tool.py
Code Highlights: 
Documentation: Đề xuất và thử nghiệm sử dụng thư viện duckduckgo, googlesearch nhưng failed do anti scrapper từ các trang web

---

## II. Debugging Case Study (10 Points)

*Analyze a specific failure event you encountered during the lab using the logging system.*

- **Problem Description**: Agent trả lời sai nghiêm trọng giá iPhone 15 128GB. Thay vì dùng dữ liệu trong kho (p001 = 22,000,000đ), Agent đưa ra giá 1.2-1.4 tỷ VND và một lần khác trả về $990.00. Đây là lỗi factuality và không bám nguồn dữ liệu nội bộ.
- **Log Source**: Trích từ `logs/2026-04-06.log`:
	```text
	2026-04-06T10:54:51 AGENT_START input="Giá iPhone 15 128GB là bao nhiêu?"
	2026-04-06T10:56:21 AGENT_END response="The price ... ranges from 1.2 to 1.4 billion VND"
	2026-04-06T10:56:21 AGENT_START input="Giá iPhone 15 128GB là bao nhiêu?"
	2026-04-06T10:57:45 AGENT_END response="Estimated price for iPhone 15 128GB: $990.00"

	Đối chứng cùng ngày:
	2026-04-06T10:16:43 TOOL_RESULT search_product("iPhone 15")
	-> p001 - iPhone 15 128GB - 22,000,000đ
	```
- **Diagnosis**: Nguyên nhân là mô hình Phi-3-mini-4k-instruct có xu hướng trả lời theo kiến thức chung khi prompt chưa bắt buộc "phải gọi tool trước khi trả giá/tồn kho". Ngoài ra, policy chọn tool chưa đủ chặt cho intent truy vấn định lượng (giá, tồn kho), dẫn đến bỏ qua `search_product` hoặc không ưu tiên dữ liệu nội bộ. Tóm lại đây là lỗi kết hợp giữa prompt + routing logic, không phải do thiếu dữ liệu.
- **Solution**: Cập nhật system prompt với quy tắc cứng: câu hỏi về giá/tồn kho bắt buộc gọi `search_product` hoặc `get_product_detail` trước khi trả lời. Thêm fallback validation: nếu câu trả lời chứa giá nhưng không có bằng chứng từ tool trong cùng turn thì chặn và yêu cầu gọi tool lại. Chuẩn hóa output template để luôn kèm product ID + giá từ observation. Giảm hallucination bằng cách thêm few-shot Thought/Action cho các câu hỏi "Giá ... bao nhiêu?" và "còn hàng không?". Sau khi áp dụng, Agent trả lời ổn định hơn ở các case iPhone 15 với giá đúng 22,000,000đ/25,000,000đ từ kho.

---

## III. Personal Insights: Chatbot vs ReAct (10 Points)

*Reflect on the reasoning capability difference.*

1.  **Reasoning**: Khối Thought giúp Agent chia bài toán thành các bước rõ ràng (xác định mục tiêu -> chọn tool -> đọc kết quả -> trả lời). Trong các truy vấn mua hàng có dữ liệu trong kho (ví dụ iPhone 15), Agent dùng search_product và trả về mã sản phẩm + giá cụ thể, trong khi Chatbot thường trả lời chung chung hoặc hỏi ngược lại nhiều câu. Vì vậy, Thought làm tăng tính định hướng hành động và giúp câu trả lời bám theo dữ liệu thật của hệ thống.
2.  **Reliability**: Agent có thể kém hơn Chatbot khi dữ liệu tool không đầy đủ hoặc khi mô hình suy luận yếu. Ví dụ có case Agent trả giá iPhone 15 128GB sai nghiêm trọng (ước lượng 1.2-1.4 tỷ VND), hoặc dừng ở trạng thái max_steps_reached khi so sánh độ mỏng/khối lượng laptop. Ngoài ra, ở một số câu đơn giản, Chatbot kết thúc nhanh và mượt hơn, còn Agent có thêm độ trễ do phải qua nhiều bước gọi tool.
3.  **Observation**: Phản hồi môi trường (observation) ảnh hưởng trực tiếp đến bước kế tiếp của Agent. Khi search_product trả về "không tìm thấy", Agent chuyển sang web_search_product khi có kết quả tồn kho/mã sản phẩm, Agent rút gọn vòng lặp và đi đến câu trả lời. Tuy nhiên, nếu observation mơ hồ hoặc nhiễu (nguồn web không chuẩn, snippet thiếu ngữ cảnh), Agent dễ bị kéo lệch hướng và sinh câu trả lời kém chính xác. Điều này cho thấy chất lượng tool output quan trọng không kém chất lượng mô hình.

---

## IV. Future Improvements (5 Points)

*How would you scale this for a production-level AI agent system?*

- **Scalability**: Tách hệ thống thành các lớp rõ ràng gồm Frontend, API Backend, và Agent Service; triển khai theo hướng stateless để có thể scale ngang bằng Docker/Kubernetes. Ngoài ra, có thể bổ sung hàng đợi (Redis/RabbitMQ) cho các tác vụ dài và cache kết quả truy vấn để giảm tải khi nhiều người dùng đồng thời.
- **Safety**: Xây dựng cơ chế guardrails đa tầng: kiểm tra input/output (prompt injection, thông tin nhạy cảm) và thêm một lớp “Supervisor” để đánh giá kế hoạch hành động trước khi thực thi các thao tác rủi ro. Toàn bộ hành vi agent cần được log để truy vết và rollback khi có sự cố.
- **Performance**: Dùng vector database để truy xuất tri thức/tool theo ngữ nghĩa (RAG + tool retrieval). Thêm cơ chế streaming response và observability để tối ưu liên tục dựa trên số liệu thực tế.

---

> [!NOTE]
> Submit this report by renaming it to `REPORT_[YOUR_NAME].md` and placing it in this folder.
