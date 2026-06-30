# Key Authors to Watch

> 以下作者每次发新论文都是重要信号。通过 arXiv `au:` 前缀搜索可自动追踪。

## Tier 1: Core Contributors (Must Track)

### Albert Gu (CMU)
- **Role**: SSM 理论奠基人，Mamba 系列核心
- **arXiv search**: `au:Gu_A`
- **Key works**: S4, Mamba, Mamba-2 (SSD), Mamba-3
- **Profile**: https://www.albertgu.info/
- **GitHub**: https://github.com/albertfgu

### Tri Dao (Together AI / Stanford)
- **Role**: FlashAttention 作者，Mamba 系列核心，FLA 生态推动者
- **arXiv search**: `au:Dao_T`
- **Key works**: FlashAttention 1/2/3, Mamba, Mamba-2, Mamba-3
- **GitHub**: https://github.com/tridao

### Aviv Bick (CMU)
- **Role**: Albert Gu 学生，专注 SSM 蒸馏、hybrid 架构、state tracking
- **arXiv search**: `au:Bick_A`
- **Key works**:
  - MOHAWK: Transformers to SSMs distillation (arXiv:2408.10189)
  - Mamba-3 (ICLR 2026, with Gu & Dao)
  - Raven: Sparse Memory Routing (ICLR 2026)
  - Gather-and-Aggregate mechanism analysis (arXiv:2504.18574)
  - Long-Context SSM Video World Models (arXiv:2505.20171)
- **Profile**: https://avivbick.github.io/
- **Twitter/X**: @avivbick

### Songlin Yang (MIT / Together AI)
- **Role**: FLA (Flash Linear Attention) 主要维护者
- **arXiv search**: `au:Yang_S`
- **Key works**: GLA, DeltaNet, Gated DeltaNet, FLA library
- **GitHub**: https://github.com/sustcsonglin

## Tier 2: Key Collaborators & Frequent Contributors

### Yoon Kim (MIT)
- **Role**: Based, Rebased, GLA 合作者
- **arXiv search**: `au:Kim_Y`
- **Key works**: Gated Linear Attention, Based/Rebased linear attention

### Christopher Ré (Stanford)
- **Role**: S4/S5, Zoology, Hedgehog & Porcupine 理论框架
- **arXiv search**: `au:Re_C`
- **Key works**: S4, Zoology, Hedgehog & Porcupine, Monarch Mixer
- **Lab**: https://hazyresearch.stanford.edu/

### Michael Zhang (Stanford)
- **Role**: Expressive linear attention, Based, Hedgehog & Porcupine
- **arXiv search**: `au:Zhang_M`
- **Key works**: Simple linear attention language models, Hedgehog & Porcupine

### J. Zico Kolter (CMU)
- **Role**: 深度学习理论，Mamba-3 合作者
- **arXiv search**: `au:Kolter_J`
- **Key works**: Mamba-3, 深度网络优化理论

### Kevin Y. Li (CMU)
- **Role**: Mamba-3 核心作者，与 Aviv Bick 密切合作
- **arXiv search**: `au:Li_KY`
- **Key works**: Mamba-3, MOHAWK

## Tier 3: Rising Contributors & Frequent Co-authors

### Berlin Chen (CMU)
- **arXiv search**: `au:Chen_B`
- **Key works**: Mamba-3

### Caitlin Wang (CMU)
- **arXiv search**: `au:Wang_C`
- **Key works**: Mamba-3

### Aakash Lahoti (CMU)
- **arXiv search**: `au:Lahoti_A`
- **Key works**: Mamba-3 (一作)

## How to Monitor

### Manual Check
```bash
# 检查某位作者最近论文
python3 scripts/daily_scan.py --author "Bick_A"
```

### arXiv Author Search Prefix
- `au:Gu_A` — Albert Gu
- `au:Dao_T` — Tri Dao
- `au:Bick_A` — Aviv Bick
- `au:Yang_S` — Songlin Yang

### Twitter/X 监控（手动）
- @albertfgu
- @tridao
- @avivbick
- @sustcsonglin
