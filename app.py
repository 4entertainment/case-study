import os
import streamlit as st
from query import retrieve
from ingest import ingest_documents
from tempfile import NamedTemporaryFile
import time

# Sayfa yapılandırması
st.set_page_config(
    layout="wide", 
    page_title="Türkçe RAG Sistemi",
    page_icon="📚",
    initial_sidebar_state="expanded"
)

# CSS ile özel stil
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .search-container {
        background: #f8f9fa;
        padding: 2rem;
        border-radius: 15px;
        border: 1px solid #e9ecef;
        margin-bottom: 2rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    
    .upload-container {
        background: #fff3cd;
        padding: 2rem;
        border-radius: 15px;
        border: 1px solid #ffeaa7;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    
    .result-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s ease;
    }
    
    .result-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }
    
    .source-tag {
        background: #667eea;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
        margin-bottom: 1rem;
        display: inline-block;
    }
    
    .metric-container {
        background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 1rem;
    }
    
    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.5rem 2rem;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    
    .info-box {
        background: #e3f2fd;
        border: 1px solid #90caf9;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Ana başlık
st.markdown("""
<div class="main-header">
    <h1>📚 Türkçe RAG Tabanlı Belge Sorgulama Sistemi</h1>
    <p>Belgelerinizi yükleyin ve akıllı arama yapın</p>
</div>
""", unsafe_allow_html=True)

# Sidebar - İstatistikler ve bilgiler
with st.sidebar:
    st.markdown("### 📊 Sistem Durumu")
    
    # Basit metrikler (gerçek verilerle değiştirebilirsiniz)
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Toplam Belge", "12", "2")
    with col2:
        st.metric("Son Sorgu", "2dk önce", "-1dk")
    
    st.markdown("---")
    st.markdown("### ℹ️ Nasıl Kullanılır?")
    st.markdown("""
    1. **PDF Yükle**: Aşağıdan PDF dosyalarınızı yükleyin
    2. **Bekleyin**: Sistem belgelerinizi işleyecek
    3. **Sorgula**: Arama kutusuna sorunuzu yazın
    4. **Sonuçları İncele**: En alakalı sonuçları görün
    """)
    
    st.markdown("---")
    st.markdown("### 🎯 İpuçları")
    st.info("Daha iyi sonuçlar için spesifik sorular sorun. Örnek: 'Proje bütçesi nedir?' yerine 'Q4 2024 proje bütçesi nedir?'")

# Ana içerik alanı
col1, col2 = st.columns([2, 1])

with col1:
    # Arama bölümü
    st.markdown('<div class="search-container">', unsafe_allow_html=True)
    st.markdown("## 🔍 Belge Arama")
    
    query = st.text_input(
        "Arama sorgunuzu girin:",
        placeholder="Örn: Şirket politikaları hakkında bilgi...",
        help="Belgelerinizde arama yapmak için sorunuzu buraya yazın"
    )
    
    col_search, col_clear = st.columns([3, 1])
    with col_search:
        search_button = st.button("🔎 Sorgula", use_container_width=True)
    with col_clear:
        if st.button("🗑️ Temizle", use_container_width=True):
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Sonuçlar bölümü
    if search_button and query:
        with st.spinner('🔄 Belgeler aranıyor...'):
            time.sleep(1)  # Görsel efekt için
            results = retrieve(query)
            
        if results:
            st.markdown(f"## 📋 Arama Sonuçları ({len(results)} sonuç bulundu)")
            
            for i, doc in enumerate(results, 1):
                st.markdown(f"""
                <div class="result-card">
                    <div class="source-tag">📄 {doc['source']}</div>
                    <div style="color: #2c3e50; line-height: 1.6;">
                        {doc['content']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning("🔍 Arama kriterlerinize uygun sonuç bulunamadı. Farklı anahtar kelimeler deneyin.")

with col2:
    # Dosya yükleme bölümü
    st.markdown('<div class="upload-container">', unsafe_allow_html=True)
    st.markdown("## 📤 PDF Dosya Yükleme")
    
    uploaded_files = st.file_uploader(
        "PDF Dosyaları Seçin",
        accept_multiple_files=True,
        type="pdf",
        help="Birden fazla PDF dosyası seçebilirsiniz"
    )
    
    if uploaded_files:
        st.markdown("### 📁 Seçilen Dosyalar:")
        for file in uploaded_files:
            st.markdown(f"• **{file.name}** ({file.size / 1024:.1f} KB)")
        
        if st.button("📥 Dosyaları İşle", use_container_width=True):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Dosyaları kaydetme
            for i, uploaded_file in enumerate(uploaded_files):
                status_text.text(f'📄 İşleniyor: {uploaded_file.name}')
                progress_bar.progress((i + 1) / len(uploaded_files))
                
                # Dosyayı geçici olarak kaydet
                os.makedirs("data/uploaded", exist_ok=True)
                with NamedTemporaryFile(delete=False, suffix=".pdf", dir="data/uploaded") as tmp:
                    tmp.write(uploaded_file.read())
                
                time.sleep(0.5)  # Görsel efekt için
            
            # Belgeleri işle
            status_text.text('🔄 Belgeler veri tabanına ekleniyor...')
            ingest_documents("data/uploaded")
            
            progress_bar.progress(100)
            status_text.empty()
            progress_bar.empty()
            
            st.success("✅ Dosyalar başarıyla yüklendi ve işleme alındı!")
            st.balloons()  # Kutlama efekti
    
    st.markdown('</div>', unsafe_allow_html=True)

# Alt bilgi
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #7f8c8d; padding: 1rem;'>
    <p>🤖 Türkçe RAG Sistemi - Akıllı Belge Arama Motoru</p>
    <p><small>Bu sistem, yüklediğiniz PDF belgelerinde semantik arama yapar.</small></p>
</div>
""", unsafe_allow_html=True)