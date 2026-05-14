package com.antigravity.stocks

import android.annotation.SuppressLint
import android.graphics.Color
import android.os.Bundle
import android.view.Gravity
import android.view.ViewGroup
import android.webkit.WebChromeClient
import android.webkit.WebResourceError
import android.webkit.WebResourceRequest
import android.webkit.WebSettings
import android.webkit.WebView
import android.webkit.WebViewClient
import android.widget.Button
import android.widget.FrameLayout
import android.widget.LinearLayout
import android.widget.ProgressBar
import android.widget.TextView
import androidx.activity.OnBackPressedCallback
import androidx.appcompat.app.AppCompatActivity
import androidx.core.view.WindowCompat
import androidx.core.view.WindowInsetsCompat
import androidx.core.view.WindowInsetsControllerCompat

class MainActivity : AppCompatActivity() {

    private lateinit var webView: WebView
    private lateinit var loadingLayout: FrameLayout
    private lateinit var errorLayout: LinearLayout

    companion object {
        private const val TARGET_URL = "https://tony-stock-news.onrender.com"
    }

    @SuppressLint("SetJavaScriptEnabled")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        setupFullScreen()

        // 루트 컨테이너 (FrameLayout으로 레이어 겹침)
        val root = FrameLayout(this).apply {
            layoutParams = ViewGroup.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.MATCH_PARENT
            )
            setBackgroundColor(Color.parseColor("#0a0a0f"))
        }

        // ── 1. 웹뷰 ──────────────────────────────────────
        webView = WebView(this).apply {
            layoutParams = FrameLayout.LayoutParams(
                FrameLayout.LayoutParams.MATCH_PARENT,
                FrameLayout.LayoutParams.MATCH_PARENT
            )
            setBackgroundColor(Color.parseColor("#0a0a0f"))

            settings.apply {
                javaScriptEnabled = true
                domStorageEnabled = true
                databaseEnabled = true
                loadWithOverviewMode = true
                useWideViewPort = true
                builtInZoomControls = false
                displayZoomControls = false
                setSupportMultipleWindows(true)
                mixedContentMode = WebSettings.MIXED_CONTENT_ALWAYS_ALLOW
                cacheMode = WebSettings.LOAD_DEFAULT
            }

            webViewClient = object : WebViewClient() {
                override fun onPageFinished(view: WebView?, url: String?) {
                    super.onPageFinished(view, url)
                    // 페이지 로드 완료 → 로딩 화면 숨김
                    loadingLayout.visibility = android.view.View.GONE
                    errorLayout.visibility = android.view.View.GONE
                    view?.visibility = android.view.View.VISIBLE
                }

                override fun onReceivedError(
                    view: WebView?,
                    request: WebResourceRequest?,
                    error: WebResourceError?
                ) {
                    super.onReceivedError(view, request, error)
                    // 메인 페이지 에러일 때만 에러 화면 표시
                    if (request?.isForMainFrame == true) {
                        loadingLayout.visibility = android.view.View.GONE
                        errorLayout.visibility = android.view.View.VISIBLE
                        view?.visibility = android.view.View.INVISIBLE
                    }
                }

                @Deprecated("Deprecated in Java")
                override fun shouldOverrideUrlLoading(view: WebView?, url: String?): Boolean {
                    if (url != null) {
                        view?.loadUrl(url)
                    }
                    return true
                }
            }
            webChromeClient = WebChromeClient()
        }

        // ── 2. 로딩 화면 ──────────────────────────────────
        loadingLayout = FrameLayout(this).apply {
            layoutParams = FrameLayout.LayoutParams(
                FrameLayout.LayoutParams.MATCH_PARENT,
                FrameLayout.LayoutParams.MATCH_PARENT
            )
            setBackgroundColor(Color.parseColor("#0a0a0f"))

            val inner = LinearLayout(context).apply {
                orientation = LinearLayout.VERTICAL
                gravity = Gravity.CENTER
                layoutParams = FrameLayout.LayoutParams(
                    FrameLayout.LayoutParams.WRAP_CONTENT,
                    FrameLayout.LayoutParams.WRAP_CONTENT,
                    Gravity.CENTER
                )

                // 스피너
                addView(ProgressBar(context).apply {
                    indeterminateTintList = android.content.res.ColorStateList.valueOf(
                        Color.parseColor("#6c63ff")
                    )
                    val size = (56 * resources.displayMetrics.density).toInt()
                    layoutParams = LinearLayout.LayoutParams(size, size).apply {
                        bottomMargin = (24 * resources.displayMetrics.density).toInt()
                    }
                })

                // 앱 이름
                addView(TextView(context).apply {
                    text = "Tony Stocks"
                    setTextColor(Color.parseColor("#e8e8f0"))
                    textSize = 20f
                    gravity = Gravity.CENTER
                    typeface = android.graphics.Typeface.DEFAULT_BOLD
                    layoutParams = LinearLayout.LayoutParams(
                        LinearLayout.LayoutParams.WRAP_CONTENT,
                        LinearLayout.LayoutParams.WRAP_CONTENT
                    ).apply {
                        bottomMargin = (8 * resources.displayMetrics.density).toInt()
                    }
                })

                // 안내 메시지
                addView(TextView(context).apply {
                    text = "서버를 깨우는 중... (최대 1분 소요)"
                    setTextColor(Color.parseColor("#8888aa"))
                    textSize = 13f
                    gravity = Gravity.CENTER
                    layoutParams = LinearLayout.LayoutParams(
                        LinearLayout.LayoutParams.WRAP_CONTENT,
                        LinearLayout.LayoutParams.WRAP_CONTENT
                    )
                })
            }
            addView(inner)
        }

        // ── 3. 에러 화면 ──────────────────────────────────
        errorLayout = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            gravity = Gravity.CENTER
            layoutParams = FrameLayout.LayoutParams(
                FrameLayout.LayoutParams.MATCH_PARENT,
                FrameLayout.LayoutParams.MATCH_PARENT
            )
            setBackgroundColor(Color.parseColor("#0a0a0f"))
            visibility = android.view.View.GONE

            // 에러 아이콘 (이모지 텍스트로 대체)
            addView(TextView(this@MainActivity).apply {
                text = "📡"
                textSize = 52f
                gravity = Gravity.CENTER
                layoutParams = LinearLayout.LayoutParams(
                    LinearLayout.LayoutParams.WRAP_CONTENT,
                    LinearLayout.LayoutParams.WRAP_CONTENT
                ).apply {
                    bottomMargin = (16 * resources.displayMetrics.density).toInt()
                }
            })

            addView(TextView(this@MainActivity).apply {
                text = "서버에 연결할 수 없습니다"
                setTextColor(Color.parseColor("#e8e8f0"))
                textSize = 18f
                gravity = Gravity.CENTER
                typeface = android.graphics.Typeface.DEFAULT_BOLD
                layoutParams = LinearLayout.LayoutParams(
                    LinearLayout.LayoutParams.WRAP_CONTENT,
                    LinearLayout.LayoutParams.WRAP_CONTENT
                ).apply {
                    bottomMargin = (8 * resources.displayMetrics.density).toInt()
                }
            })

            addView(TextView(this@MainActivity).apply {
                text = "인터넷 연결을 확인하거나\n잠시 후 다시 시도해주세요"
                setTextColor(Color.parseColor("#8888aa"))
                textSize = 13f
                gravity = Gravity.CENTER
                layoutParams = LinearLayout.LayoutParams(
                    LinearLayout.LayoutParams.WRAP_CONTENT,
                    LinearLayout.LayoutParams.WRAP_CONTENT
                ).apply {
                    bottomMargin = (32 * resources.displayMetrics.density).toInt()
                }
            })

            // 재시도 버튼
            addView(Button(this@MainActivity).apply {
                text = "다시 시도"
                setTextColor(Color.WHITE)
                setBackgroundColor(Color.parseColor("#6c63ff"))
                textSize = 15f
                val pd = (20 * resources.displayMetrics.density).toInt()
                val pdV = (12 * resources.displayMetrics.density).toInt()
                setPadding(pd, pdV, pd, pdV)
                layoutParams = LinearLayout.LayoutParams(
                    LinearLayout.LayoutParams.WRAP_CONTENT,
                    LinearLayout.LayoutParams.WRAP_CONTENT
                )
                setOnClickListener {
                    errorLayout.visibility = android.view.View.GONE
                    loadingLayout.visibility = android.view.View.VISIBLE
                    webView.visibility = android.view.View.INVISIBLE
                    webView.reload()
                }
            })
        }

        // 레이어 순서: 웹뷰 → 로딩 → 에러 (위에 쌓임)
        root.addView(webView)
        root.addView(loadingLayout)
        root.addView(errorLayout)

        setContentView(root)
        webView.loadUrl(TARGET_URL)

        // 뒤로가기
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

    private fun setupFullScreen() {
        WindowCompat.setDecorFitsSystemWindows(window, false)
        WindowInsetsControllerCompat(window, window.decorView).apply {
            hide(WindowInsetsCompat.Type.systemBars())
            systemBarsBehavior = WindowInsetsControllerCompat.BEHAVIOR_SHOW_TRANSIENT_BARS_BY_SWIPE
        }
    }
}
