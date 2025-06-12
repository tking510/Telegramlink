// ゲーム統計とロジック管理クラス (フロントエンド用)
// このファイルは、バックエンドと連携するように変更されています。
// 以前の静的ファイル版とは異なり、API経由でデータをやり取りします。

class SlotGameManager {
    constructor(userId) {
        this.userId = userId;
        this.symbols = [
            { name: \'cherry\', src: \'https://www.svgrepo.com/show/499364/cherry.svg\' },
            { name: \'lemon\', src: \'https://www.svgrepo.com/show/499365/lemon.svg\' },
            { name: \'orange\', src: \'https://www.svgrepo.com/show/499366/orange.svg\' },
            { name: \'grape\', src: \'https://www.svgrepo.com/show/499363/grape.svg\' },
            { name: \'bell\', src: \'https://www.svgrepo.com/show/499362/bell.svg\' },
            { name: \'bar\', src: \'https://www.svgrepo.com/show/499361/bar.svg\' },
            { name: \'seven\', src: \'https://www.svgrepo.com/show/499367/seven.svg\' }
        ];
        this.API_BASE_URL = window.location.origin + \'/api\';
    }

    getSymbols( ) {
        return this.symbols;
    }

    getSymbolIndex(symbolName) {
        return this.symbols.findIndex(s => s.name === symbolName);
    }

    async spin() {
        try {
            const response = await fetch(`${this.API_BASE_URL}/spin`, {
                method: \'POST\',
                headers: { \'Content-Type\': \'application/json\' },
                body: JSON.stringify({ user_id: this.userId })
            });
            const data = await response.json();
            if (response.ok) {
                return data.result; // message, code, type, symbols
            } else {
                // エラーメッセージを返す
                return { message: data.message || data.error || \'スピンに失敗しました。\', code: null, type: \'error\', symbols: null };
            }
        } catch (error) {
            console.error(\'Error during spin:\', error);
            return { message: \'通信エラーが発生しました。\', code: null, type: \'error\', symbols: null };
        }
    }

    async checkUserPlayStatus() {
        try {
            const response = await fetch(`${this.API_BASE_URL}/users/${this.userId}`);
            const data = await response.json();
            if (response.ok) {
                return data.user.played_at !== null;
            } else if (response.status === 404) {
                // ユーザーが見つからない場合
                return false;
            } else {
                console.error(\'Error checking user status:\', data.error);
                return false; // エラー時は未プレイとして扱うか、適切なハンドリング
            }
        } catch (error) {
            console.error(\'Error checking user status:\', error);
            return false;
        }
    }
}
