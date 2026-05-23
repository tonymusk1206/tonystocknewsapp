package com.antigravity.stocks

import android.annotation.SuppressLint
import android.content.Intent
import android.graphics.Color
import android.net.Uri
import android.net.http.SslError
import android.os.Build
import android.os.Bundle
import android.view.ViewGroup
import android.webkit.SslErrorHandler
import android.webkit.WebChromeClient
import android.webkit.WebResourceRequest
import android.webkit.WebSettings
import android.webkit.WebView
import android.webkit.WebViewClient
import androidx.activity.OnBackPressedCallback
import androidx.appcompat.app.AppCompatActivity
import androidx.core.view.WindowCompat
import androidx.core.view.WindowInsetsCompat
import androidx.core.view.WindowInsetsControllerCompat

class MainActivity : AppCompatActivity() {

    private lateinit var webView: WebView

    companion object {
        private const val TARGET_URL = "https://tony-stock-news.onrender.com"
    }

    @SuppressLint("SetJavaScriptEnabled")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // 전체화면 (상태바 및 네비게이션바 숨김 처리)
        setupFullScreen()

        // 웹뷰 크롬 디버깅 활성화 (PC 크롬 브라우저 chrome://inspect 에서 앱 내 로그 분석 가능)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.KITKAT) {
            WebView.setWebContentsDebuggingEnabled(true)
        }

        // 웹뷰 생성 및 설정
        webView = WebView(this).apply {
            layoutParams = ViewGroup.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.MATCH_PARENT
            )
            setBackgroundColor(Color.parseColor("#0a0a0f")) // 웹앱 배경색과 동일하게 맞춤
            
            settings.apply {
                javaScriptEnabled = true
                domStorageEnabled = true
                databaseEnabled = true
                allowFileAccess = true // 로컬 파일 액세스 허용
                loadWithOverviewMode = true
                useWideViewPort = true
                builtInZoomControls = false
                displayZoomControls = false
                setSupportMultipleWindows(false) // 팝업/새창으로 인한 렌더링 멈춤 방지
                mixedContentMode = WebSettings.MIXED_CONTENT_ALWAYS_ALLOW
                cacheMode = WebSettings.LOAD_DEFAULT
            }

            webViewClient = object : WebViewClient() {
                // 최신 API 24 이상 버전용 URL 라우팅 핸들러
                override fun shouldOverrideUrlLoading(view: WebView?, request: WebResourceRequest?): Boolean {
                    val url = request?.url?.toString() ?: return false
                    return handleUrlRouting(view, url)
                }

                // 구형 API 버전 호환용 URL 라우팅 핸들러
                @Deprecated("Deprecated in Java")
                override fun shouldOverrideUrlLoading(view: WebView?, url: String?): Boolean {
                    if (url != null) {
                        return handleUrlRouting(view, url)
                    }
                    return false
                }

                // SSL 인증서 문제 발생 시 개발/테스트 목적의 우회 로직 (Render.com 인증서 딜레이나 만료 이슈 대응)
                @SuppressLint("WebViewClientOnReceivedSslError")
                override fun onReceivedSslError(view: WebView?, handler: SslErrorHandler?, error: SslError?) {
                    handler?.proceed() // 주의: 상용 릴리즈 시에는 보안 검토 필요
                }
            }
            webChromeClient = WebChromeClient()
        }

        setContentView(webView)
        webView.loadUrl(TARGET_URL)

        // 뒤로가기 버튼 제어
        onBackPressedDispatcher.addCallback(this, object : OnBackPressedCallback(true) {
            override fun handleOnBackPressed() {
                if (webView.canGoBack()) {
                    webView.goBack()
                } else {
                    finish()
                }
            }
        })
    }

    // 내부 URL은 웹뷰 안에서 열고, 외부 URL(유튜브, 외부 뉴스 등)은 외부 브라우저(인텐트)로 라우팅
    private fun handleUrlRouting(view: WebView?, url: String): Boolean {
        // 내부 웹앱 URL 도메인인 경우 웹뷰 안에서 탐색 수행 (false 리턴 -> 기본 동작 실행)
        if (url.startsWith(TARGET_URL) || url.contains("onrender.com")) {
            return false
        }
        
        // 그 외 외부 링크(유튜브, 뉴스 등)는 외부 브라우저 인텐트로 전달
        try {
            val intent = Intent(Intent.ACTION_VIEW, Uri.parse(url))
            startActivity(intent)
            return true // 앱에서 인텐트를 직접 처리했으므로 true 리턴
        } catch (e: Exception) {
            // 인텐트 실행 실패 시 웹뷰 내에서 열리도록 폴백
            return false
        }
    }

    private fun setupFullScreen() {
        WindowCompat.setDecorFitsSystemWindows(window, false)
        WindowInsetsControllerCompat(window, window.decorView).apply {
            hide(WindowInsetsCompat.Type.systemBars())
            systemBarsBehavior = WindowInsetsControllerCompat.BEHAVIOR_SHOW_TRANSIENT_BARS_BY_SWIPE
        }
    }
}
