// ゲーム統計とロジック管理クラス
class SlotGameManager {
    constructor() {
        this.config = null;
        this.statistics = {
            totalSpins: 0,
            wins: {
                jackpot: 0,
                bigWin: 0,
                smallWin: 0
            },
            codesGenerated: []
        };
        this.loadConfig();
    }

    // 設定ファイルの読み込み
    async loadConfig() {
        try {
            const response = await fetch('config.json');
            this.config = await response.json();
            console.log('設定ファイルが読み込まれました:', this.config);
        } catch (error) {
            console.error('設定ファイルの読み込みに失敗しました:', error);
            // デフォルト設定を使用
            this.config = {
                probabilities: {
                    jackpot: 0.01,
                    bigWin: 0.05,
                    smallWin: 0.15,
                    lose: 0.79
                },
                winPatterns: {
                    jackpot: {
                        message: "🎉 JACKPOT! 🎉",
                        codePrefix: "JP",
                        multiplier: 1000,
                        description: "全て同じ絵柄"
                    },
                    bigWin: {
                        message: "🎊 BIG WIN! 🎊",
                        codePrefix: "BW",
                        multiplier: 100,
                        description: "2つ同じ絵柄"
                    },
                    smallWin: {
                        message: "✨ WIN! ✨",
                        codePrefix: "SW",
                        multiplier: 10,
                        description: "特定の組み合わせ"
                    }
                },
                symbols: ['🍒', '🍋', '🍊', '🍇', '🔔', '⭐', '💎', '7️⃣'],
                gameSettings: {
                    spinDuration: 2000,
                    reelStopDelay: 500,
                    animationSpeed: 20
                }
            };
        }
    }

    // 確率設定の更新
    updateProbabilities(newProbabilities) {
        if (this.config) {
            this.config.probabilities = { ...this.config.probabilities, ...newProbabilities };
            console.log('確率が更新されました:', this.config.probabilities);
        }
    }

    // 当選判定（重み付きランダム）
    determineResult() {
        const rand = Math.random();
        const probs = this.config.probabilities;
        
        let cumulative = 0;
        for (const [type, probability] of Object.entries(probs)) {
            cumulative += probability;
            if (rand < cumulative) {
                return type;
            }
        }
        
        return 'lose'; // フォールバック
    }

    // より高度なコード生成
    generateCode(type) {
        const pattern = this.config.winPatterns[type];
        if (!pattern) return null;

        const timestamp = Date.now().toString().slice(-6);
        const random = Math.random().toString(36).substring(2, 6).toUpperCase();
        const checksum = this.calculateChecksum(timestamp + random);
        const code = `${pattern.codePrefix}${timestamp}${random}${checksum}`;
        
        // 統計に記録
        this.statistics.codesGenerated.push({
            code: code,
            type: type,
            timestamp: new Date().toISOString()
        });
        
        return code;
    }

    // チェックサム計算（簡単な検証用）
    calculateChecksum(str) {
        let sum = 0;
        for (let i = 0; i < str.length; i++) {
            sum += str.charCodeAt(i);
        }
        return (sum % 36).toString(36).toUpperCase();
    }

    // 結果に基づくシンボル設定
    setResultSymbols(result) {
        const symbols = this.config.symbols;
        let finalSymbols = [];
        
        switch (result) {
            case 'jackpot':
                // 全て同じシンボル（高価値シンボル優先）
                const jackpotSymbol = this.getHighValueSymbol();
                finalSymbols = [jackpotSymbol, jackpotSymbol, jackpotSymbol];
                break;
                
            case 'bigWin':
                // 2つ同じシンボル
                const winSymbol = symbols[Math.floor(Math.random() * symbols.length)];
                const otherSymbol = symbols[Math.floor(Math.random() * symbols.length)];
                finalSymbols = [winSymbol, winSymbol, otherSymbol];
                break;
                
            case 'smallWin':
                // 特定の組み合わせパターン
                const smallWinPatterns = [
                    ['🍒', '🍋', '🍒'],
                    ['🔔', '🔔', '⭐'],
                    ['🍇', '🍊', '🍇']
                ];
                finalSymbols = smallWinPatterns[Math.floor(Math.random() * smallWinPatterns.length)];
                break;
                
            default:
                // ランダム（ハズレ）
                finalSymbols = this.generateLosingCombination();
                break;
        }
        
        return finalSymbols;
    }

    // 高価値シンボルの取得
    getHighValueSymbol() {
        const highValueSymbols = ['💎', '7️⃣', '⭐'];
        return highValueSymbols[Math.floor(Math.random() * highValueSymbols.length)];
    }

    // ハズレの組み合わせ生成
    generateLosingCombination() {
        const symbols = this.config.symbols;
        let combination;
        
        do {
            combination = [
                symbols[Math.floor(Math.random() * symbols.length)],
                symbols[Math.floor(Math.random() * symbols.length)],
                symbols[Math.floor(Math.random() * symbols.length)]
            ];
        } while (this.isWinningCombination(combination));
        
        return combination;
    }

    // 当選組み合わせかどうかの判定
    isWinningCombination(symbols) {
        // 全て同じ
        if (symbols[0] === symbols[1] && symbols[1] === symbols[2]) {
            return true;
        }
        
        // 2つ同じ
        if (symbols[0] === symbols[1] || symbols[1] === symbols[2] || symbols[0] === symbols[2]) {
            return true;
        }
        
        // 特定のパターン
        const winPatterns = [
            ['🍒', '🍋', '🍒'],
            ['🔔', '🔔', '⭐'],
            ['🍇', '🍊', '🍇']
        ];
        
        return winPatterns.some(pattern => 
            pattern[0] === symbols[0] && 
            pattern[1] === symbols[1] && 
            pattern[2] === symbols[2]
        );
    }

    // 統計の更新
    updateStatistics(result) {
        this.statistics.totalSpins++;
        if (result !== 'lose') {
            this.statistics.wins[result]++;
        }
    }

    // 統計の取得
    getStatistics() {
        const winRate = this.statistics.totalSpins > 0 ? 
            (Object.values(this.statistics.wins).reduce((a, b) => a + b, 0) / this.statistics.totalSpins * 100).toFixed(2) : 0;
        
        return {
            ...this.statistics,
            winRate: winRate + '%'
        };
    }

    // 設定の保存（ローカルストレージ）
    saveConfig() {
        localStorage.setItem('slotGameConfig', JSON.stringify(this.config));
        localStorage.setItem('slotGameStats', JSON.stringify(this.statistics));
    }

    // 設定の読み込み（ローカルストレージ）
    loadSavedConfig() {
        const savedConfig = localStorage.getItem('slotGameConfig');
        const savedStats = localStorage.getItem('slotGameStats');
        
        if (savedConfig) {
            this.config = JSON.parse(savedConfig);
        }
        
        if (savedStats) {
            this.statistics = JSON.parse(savedStats);
        }
    }
}

// グローバルなゲームマネージャーインスタンス
const gameManager = new SlotGameManager();

