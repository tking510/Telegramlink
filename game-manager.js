// ゲーム統計とロジック管理クラス
class SlotGameManager {
    constructor() {
        this.config = this.loadConfig();
        this.symbols = [
            { name: 'cherry', src: 'https://www.svgrepo.com/show/499364/cherry.svg' },
            { name: 'lemon', src: 'https://www.svgrepo.com/show/499365/lemon.svg' },
            { name: 'orange', src: 'https://www.svgrepo.com/show/499366/orange.svg' },
            { name: 'grape', src: 'https://www.svgrepo.com/show/499363/grape.svg' },
            { name: 'bell', src: 'https://www.svgrepo.com/show/499362/bell.svg' },
            { name: 'bar', src: 'https://www.svgrepo.com/show/499361/bar.svg' },
            { name: 'seven', src: 'https://www.svgrepo.com/show/499367/seven.svg' }
        ];
    }

    // 設定をロード（ローカルストレージ優先 ）
    loadConfig() {
        const savedConfig = localStorage.getItem('slotGameConfig');
        if (savedConfig) {
            return JSON.parse(savedConfig);
        } else {
            // デフォルト設定 (config.jsonの内容を直接記述)
            return {
                probabilities: {
                    jackpot: 1.0,   // 全て同じ絵柄
                    bigWin: 5.0,    // 2つ同じ絵柄
                    smallWin: 15.0, // 特定の組み合わせ（例: チェリーが1つでもあれば）
                    lose: 79.0      // ハズレ
                },
                stats: {
                    totalPlays: 0,
                    jackpotCount: 0,
                    bigWinCount: 0,
                    smallWinCount: 0,
                    loseCount: 0
                },
                codeHistory: []
            };
        }
    }

    // 設定を保存
    saveConfig() {
        localStorage.setItem('slotGameConfig', JSON.stringify(this.config));
    }

    // シンボルリストを取得
    getSymbols() {
        return this.symbols;
    }

    // シンボル名からインデックスを取得
    getSymbolIndex(symbolName) {
        return this.symbols.findIndex(s => s.name === symbolName);
    }

    // スピン処理
    spin() {
        this.config.stats.totalPlays++;
        this.saveConfig();

        const results = [];
        for (let i = 0; i < 3; i++) {
            results.push(this.getRandomSymbol());
        }
        return results;
    }

    // 確率に基づいてランダムな結果を生成
    getRandomSymbol() {
        const rand = Math.random() * 100;
        let cumulativeProbability = 0;

        // 確率の合計が100%になるように調整
        const totalProb = this.config.probabilities.jackpot +
                          this.config.probabilities.bigWin +
                          this.config.probabilities.smallWin +
                          this.config.probabilities.lose;

        // 確率が設定されていない、または合計が0の場合はデフォルトのハズレとする
        if (totalProb === 0) {
            return this.symbols[Math.floor(Math.random() * this.symbols.length)]; // ランダムなシンボルを返す
        }

        // 確率に基づいて結果を決定
        // ここでは、最終的な絵柄の組み合わせを決定するのではなく、
        // 当選タイプ（ジャックポット、ビッグウィンなど）を決定し、
        // そのタイプに合う絵柄をランダムに選ぶロジックに簡略化しています。
        // より厳密なスロットロジックには、各リールの停止位置とシンボルのマッピングが必要です。

        // 簡単な実装として、ここでは当選タイプに基づいてランダムな絵柄を返します。
        // 実際の絵柄の組み合わせは、checkWinで判定します。

        // 常にランダムなシンボルを返すように変更
        return this.symbols[Math.floor(Math.random() * this.symbols.length)];
    }

    // 当選判定
    checkWin(finalSymbols) {
        const s1 = finalSymbols[0].name;
        const s2 = finalSymbols[1].name;
        const s3 = finalSymbols[2].name;

        let result = { message: '残念！ハズレ', code: null, type: 'lose' };

        // 全て同じ絵柄 (ジャックポット)
        if (s1 === s2 && s2 === s3) {
            this.config.stats.jackpotCount++;
            result = { message: '🎉 ジャックポット！ 🎉', code: this.generateCode('JP'), type: 'jackpot' };
        }
        // 2つ同じ絵柄 (ビッグウィン) - 例: 最初の2つ、最後の2つ、最初と最後
        else if (s1 === s2 || s2 === s3 || s1 === s3) {
            this.config.stats.bigWinCount++;
            result = { message: '✨ ビッグウィン！ ✨', code: this.generateCode('BW'), type: 'bigWin' };
        }
        // 特定の組み合わせ (スモールウィン) - 例: チェリーが1つでもあれば
        else if (s1 === 'cherry' || s2 === 'cherry' || s3 === 'cherry') {
            this.config.stats.smallWinCount++;
            result = { message: '🍒 スモールウィン！ 🍒', code: this.generateCode('SW'), type: 'smallWin' };
        }
        else {
            this.config.stats.loseCount++;
        }

        this.addCodeToHistory(result.code, result.type);
        this.saveConfig();
        return result;
    }

    // 特典コード生成
    generateCode(prefix) {
        const timestamp = Date.now().toString(36);
        const randomStr = Math.random().toString(36).substring(2, 8); // 6桁のランダム文字列
        const rawCode = `${prefix}-${timestamp}-${randomStr}`.toUpperCase();
        const checksum = this.generateChecksum(rawCode);
        return `${rawCode}-${checksum}`;
    }

    // チェックサム生成 (簡易的なもの)
    generateChecksum(str) {
        let sum = 0;
        for (let i = 0; i < str.length; i++) {
            sum += str.charCodeAt(i);
        }
        return (sum % 100).toString().padStart(2, '0'); // 2桁のチェックサム
    }

    // チェックサム検証 (簡易的なもの)
    verifyCode(code) {
        const parts = code.split('-');
        if (parts.length < 4) return false;
        const rawCode = parts.slice(0, -1).join('-');
        const receivedChecksum = parts[parts.length - 1];
        return this.generateChecksum(rawCode) === receivedChecksum;
    }

    // 確率設定を更新
    updateProbabilities(newProbabilities) {
        this.config.probabilities = newProbabilities;
        this.saveConfig();
    }

    // 現在の確率設定を取得
    getProbabilities() {
        return this.config.probabilities;
    }

    // 統計情報を取得
    getStats() {
        const totalPlays = this.config.stats.totalPlays;
        const winCount = this.config.stats.jackpotCount + this.config.stats.bigWinCount + this.config.stats.smallWinCount;
        const winRate = totalPlays > 0 ? (winCount / totalPlays) * 100 : 0;
        return {
            ...this.config.stats,
            winRate: winRate
        };
    }

    // 統計情報をリセット
    resetStats() {
        this.config.stats = {
            totalPlays: 0,
            jackpotCount: 0,
            bigWinCount: 0,
            smallWinCount: 0,
            loseCount: 0
        };
        this.config.codeHistory = []; // 履歴もリセット
        this.saveConfig();
    }

    // コード履歴に追加
    addCodeToHistory(code, type) {
        if (code) {
            this.config.codeHistory.push({
                code: code,
                type: type,
                timestamp: Date.now()
            });
            // 履歴が長くなりすぎないように最新の100件を保持
            if (this.config.codeHistory.length > 100) {
                this.config.codeHistory = this.config.codeHistory.slice(-100);
            }
            this.saveConfig();
        }
    }

    // コード履歴を取得
    getCodeHistory() {
        return this.config.codeHistory;
    }
}
