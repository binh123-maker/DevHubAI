# 3. Activity Diagram

## 3.1 Activity Diagram — Đăng ký & Đăng nhập

```mermaid
flowchart TD
    Start([Bắt đầu]) --> Choice{Chọn hành động}
    
    Choice -->|Đăng ký| RegForm[Nhập Email, Password, Họ tên]
    Choice -->|Đăng nhập| LoginForm[Nhập Email, Password]
    Choice -->|Google OAuth| GoogleAuth[Redirect Google]
    Choice -->|Quên MK| ForgotForm[Nhập Email]

    RegForm --> ValidateReg{Validation OK?}
    ValidateReg -->|Không| RegError[Hiển thị lỗi]
    RegError --> RegForm
    ValidateReg -->|Có| CheckEmail{Email tồn tại?}
    CheckEmail -->|Có| EmailExists[Lỗi: Email đã tồn tại]
    EmailExists --> RegForm
    CheckEmail -->|Không| HashPwd[Mã hóa password bcrypt]
    HashPwd --> CreateUser[Tạo user + profile]
    CreateUser --> GenJWT[Tạo JWT token]
    GenJWT --> Dashboard[Chuyển Dashboard]

    LoginForm --> ValidateLogin{Credentials hợp lệ?}
    ValidateLogin -->|Không| LoginError[Lỗi đăng nhập]
    LoginError --> LoginForm
    ValidateLogin -->|Có| CheckLocked{Tài khoản bị khóa?}
    CheckLocked -->|Có| LockedError[Lỗi: Tài khoản bị khóa]
    CheckLocked -->|Không| GenJWT

    GoogleAuth --> GoogleCallback[Nhận OAuth callback]
    GoogleCallback --> CheckGoogleUser{User tồn tại?}
    CheckGoogleUser -->|Không| CreateOAuthUser[Tạo user từ Google data]
    CheckGoogleUser -->|Có| GenJWT
    CreateOAuthUser --> GenJWT

    ForgotForm --> SendEmail[Gửi email reset token]
    SendEmail --> EmailSent[Thông báo đã gửi email]
    EmailSent --> End([Kết thúc])

    Dashboard --> End
```

## 3.2 Activity Diagram — Upload & Xử lý Tài liệu

```mermaid
flowchart TD
    Start([User chọn Upload]) --> SelectWS[Chọn Workspace/Folder]
    SelectWS --> SelectFile[Chọn file]
    SelectFile --> ValidateFile{File hợp lệ?}
    
    ValidateFile -->|Không| FileError[Lỗi: Loại/kích thước không hợp lệ]
    FileError --> SelectFile
    
    ValidateFile -->|Có| UploadFile[Upload lên server]
    UploadFile --> SaveMeta[Lưu metadata vào DB]
    SaveMeta --> QueueJob[Đưa vào background queue]
    QueueJob --> ShowProgress[Hiển thị progress bar]
    
    ShowProgress --> DetectType{Xác định loại file}
    
    DetectType -->|PDF| ExtractPDF[PyMuPDF extract]
    DetectType -->|DOCX/DOC| ExtractDocx[python-docx extract]
    DetectType -->|XLSX/CSV| ExtractExcel[pandas extract]
    DetectType -->|PPTX| ExtractPptx[python-pptx extract]
    DetectType -->|MD/TXT| ExtractText[Đọc trực tiếp]
    DetectType -->|HTML/JSON| ExtractHTML[BeautifulSoup parse]
    
    ExtractPDF --> ConvertMD[Chuyển sang Markdown]
    ExtractDocx --> ConvertMD
    ExtractExcel --> ConvertMD
    ExtractPptx --> ConvertMD
    ExtractText --> ConvertMD
    ExtractHTML --> ConvertMD
    
    ConvertMD --> SplitChunks[Chia thành chunks<br/>với page/line metadata]
    SplitChunks --> IndexFTS[Tạo full-text search index]
    IndexFTS --> UpdateStatus[Cập nhật status = processed]
    UpdateStatus --> Notify[Thông báo hoàn thành]
    Notify --> End([Kết thúc])
```

## 3.3 Activity Diagram — AI Chat với Citation

```mermaid
flowchart TD
    Start([User gửi câu hỏi]) --> SelectScope{Chọn phạm vi chat}
    
    SelectScope -->|Global| SearchAll[Tìm toàn bộ KB]
    SelectScope -->|Workspace| SearchWS[Tìm trong Workspace]
    SelectScope -->|Folder| SearchFolder[Tìm trong Folder]
    SelectScope -->|Document| SearchDoc[Tìm trong Document]
    
    SearchAll --> FTS[PostgreSQL Full-Text Search]
    SearchWS --> FTS
    SearchFolder --> FTS
    SearchDoc --> FTS
    
    FTS --> RankResults[Xếp hạng kết quả theo relevance]
    RankResults --> HasResults{Có kết quả?}
    
    HasResults -->|Không| NoData[Trả lời: Không tìm thấy<br/>thông tin trong KB]
    HasResults -->|Có| BuildContext[Xây dựng context<br/>kèm source metadata]
    
    BuildContext --> CallGemini[Gọi Gemini API<br/>với system prompt + context]
    CallGemini --> ParseResponse[Parse câu trả lời AI]
    ParseResponse --> ExtractCitations[Trích xuất citations<br/>từ source metadata]
    ExtractCitations --> SaveMessage[Lưu chat_message + citations]
    SaveMessage --> DisplayAnswer[Hiển thị câu trả lời<br/>+ danh sách nguồn]
    
    DisplayAnswer --> UserAction{User action?}
    UserAction -->|Mở nguồn| OpenSource[Mở document viewer<br/>nhảy đến page/line]
    UserAction -->|Tiếp tục chat| Start
    UserAction -->|Kết thúc| End([Kết thúc])
    
    NoData --> SaveMessage
    OpenSource --> Start
```

## 3.4 Activity Diagram — Crawl Website

```mermaid
flowchart TD
    Start([User nhập URL]) --> ValidateURL{URL hợp lệ?}
    ValidateURL -->|Không| URLError[Lỗi URL]
    URLError --> Start
    ValidateURL -->|Có| CheckDuplicate{URL đã tồn tại?}
    CheckDuplicate -->|Có| AskUpdate{User muốn cập nhật?}
    AskUpdate -->|Không| End([Kết thúc])
    AskUpdate -->|Có| FetchPage
    CheckDuplicate -->|Không| FetchPage[HTTP GET trang web]
    
    FetchPage --> FetchOK{Request thành công?}
    FetchOK -->|Không| FetchError[Lỗi crawl]
    FetchError --> End
    FetchOK -->|Có| ParseHTML[BeautifulSoup parse HTML]
    ParseHTML --> ExtractHeadings[Trích xuất Headings h1-h6]
    ExtractHeadings --> ExtractParagraphs[Trích xuất Paragraphs]
    ExtractParagraphs --> ConvertMD[Chuyển thành Markdown]
    ConvertMD --> SaveWebsite[Lưu website + contents]
    SaveWebsite --> IndexFTS[Tạo FTS index]
    IndexFTS --> ShowPreview[Hiển thị preview nội dung]
    ShowPreview --> End
```

## 3.5 Activity Diagram — Đăng xuất

```mermaid
flowchart TD
    Start([User click Đăng xuất]) --> ShowPopup[Hiển thị popup xác nhận<br/>'Bạn có chắc chắn muốn đăng xuất?']
    ShowPopup --> UserChoice{User chọn?}
    UserChoice -->|Hủy| ClosePopup[Đóng popup]
    ClosePopup --> End([Tiếp tục sử dụng])
    UserChoice -->|Đăng xuất| InvalidateToken[Xóa JWT khỏi storage]
    InvalidateToken --> ClearState[Clear React Query cache]
    ClearState --> RedirectLogin[Redirect về Login]
    RedirectLogin --> End2([Kết thúc])
```

## 3.6 Activity Diagram — Sinh Flashcard/Quiz

```mermaid
flowchart TD
    Start([User chọn tài liệu]) --> SelectAction{Chọn hành động}
    
    SelectAction -->|Flashcard| GetChunksFC[Lấy document chunks]
    SelectAction -->|Quiz| GetChunksQZ[Lấy document chunks]
    SelectAction -->|Summary| GetChunksSM[Lấy document chunks]
    
    GetChunksFC --> BuildPromptFC[Tạo prompt sinh Flashcard]
    GetChunksQZ --> BuildPromptQZ[Tạo prompt sinh Quiz]
    GetChunksSM --> BuildPromptSM[Tạo prompt tóm tắt]
    
    BuildPromptFC --> CallGemini[Gọi Gemini API]
    BuildPromptQZ --> CallGemini
    BuildPromptSM --> CallGemini
    
    CallGemini --> ParseFC[Parse Q&A pairs]
    CallGemini --> ParseQZ[Parse câu hỏi trắc nghiệm]
    CallGemini --> ParseSM[Parse summary text]
    
    ParseFC --> SaveFC[Lưu flashcards vào DB]
    ParseQZ --> SaveQZ[Lưu quizzes vào DB]
    ParseSM --> DisplaySM[Hiển thị summary]
    
    SaveFC --> DisplayFC[Hiển thị flashcards<br/>flip card UI]
    SaveQZ --> DisplayQZ[Hiển thị quiz UI]
    
    DisplayFC --> End([Kết thúc])
    DisplayQZ --> End
    DisplaySM --> End
```
