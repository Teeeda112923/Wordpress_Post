<?php
/**
 * Plugin Name: Rank Math REST Meta Exposer
 * Description: Rank Math のSEOメタ（フォーカスキーワード等）を WordPress REST API 経由で
 *              読み書きできるように登録する。wp_auto_post.py から rank_math_focus_keyword を
 *              設定するために必要。
 * Version:     1.0.0
 *
 * 設置方法（どちらか）:
 *   A) このファイルを wp-content/mu-plugins/rank-math-rest-meta.php として設置する
 *      （mu-plugins は自動有効化。フォルダが無ければ作成）
 *   B) 内容の add_action(...) 部分を、使用中のスニペット管理プラグイン（Code Snippets 等）に
 *      「PHP・どこでも実行」で登録する
 *
 * ※ Rank Math と REST API の仕様上、これらのメタは既定で show_in_rest 登録されていないため、
 *    未登録のままだと REST 経由の値（rank_math_focus_keyword 等）は WordPress 側で無視される。
 */

if (!defined('ABSPATH')) {
    exit;
}

add_action('init', function () {
    $keys = array(
        'rank_math_focus_keyword',
        'rank_math_title',
        'rank_math_description',
        'rank_math_canonical_url',
    );

    foreach ($keys as $key) {
        register_post_meta('post', $key, array(
            'type'          => 'string',
            'single'        => true,
            'show_in_rest'  => true,
            'auth_callback' => function () {
                return current_user_can('edit_posts');
            },
        ));
    }
});
