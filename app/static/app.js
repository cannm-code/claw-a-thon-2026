function chatApp() {
  return {
    // ── State ────────────────────────────────────────────────────────────────
    messages: [],
    input: '',
    loading: false,
    panel: 'chat',          // 'chat' | 'checkout' | 'confirmed' | 'history'
    handoff: {},
    passenger: { name: '', email: '', phone: '' },
    errors: {},
    selectedPayment: 'zalopay',
    bookingLoading: false,
    bookingRef: '',
    confirmedSummary: '',
    confirmedPrice: '',
    toast: '',
    _toastTimer: null,
    historyBookings: [],
    historyLoading: false,
    historyError: false,
    expandedBooking: null,

    paymentMethods: [
      { id: 'zalopay', label: 'ZaloPay', icon: '💙' },
      { id: 'vnpay', label: 'VNPay', icon: '🔴' },
      { id: 'card', label: 'Thẻ quốc tế', icon: '💳' },
    ],

    // ── Init ─────────────────────────────────────────────────────────────────
    init() {
      const saved = this._loadMessages();
      if (saved && saved.length > 0) {
        this.messages = saved;
      } else {
        this.pushWelcome();
      }
      this.$watch('messages', () => {
        this._saveMessages();
        this.$nextTick(() => this.scrollBottom());
      });
      this.$watch('loading', () => {
        this.$nextTick(() => this.scrollBottom());
      });
    },

    _saveMessages() {
      try {
        localStorage.setItem('claw-chat-messages', JSON.stringify(this.messages));
      } catch (_) {}
    },

    _loadMessages() {
      try {
        const raw = localStorage.getItem('claw-chat-messages');
        return raw ? JSON.parse(raw) : null;
      } catch (_) {
        return null;
      }
    },

    pushWelcome() {
      this.messages.push({
        role: 'assistant',
        text: 'Yo! Mình là Hannah — "em gái" du lịch của Claw-a-thon Travel ✈️🔥\n\nMình giúp bạn săn deal **vé máy bay**, **xe khách**, **tàu hỏa**, **khách sạn**, hoặc **vé tham quan** nhanh gọn lẹ!\n\nTrip tiếp theo của bạn là đâu vậy? 👀',
        structured: null,
      });
    },

    // ── Send message ─────────────────────────────────────────────────────────
    async sendMessage() {
      const text = this.input.trim();
      if (!text || this.loading) return;
      this.input = '';
      this._appendUserMsg(text);
      await this._callChat(text);
    },

    async sendChip(value) {
      if (this.loading) return;
      this._appendUserMsg(value);
      await this._callChat(value);
    },

    async selectOption(opt) {
      const msg = `Tôi chọn ${opt.title}`;
      this._appendUserMsg(msg);
      await this._callChat(msg);
    },

    _appendUserMsg(text) {
      this.messages.push({ role: 'user', text, structured: null });
    },

    async _fetchChat(text) {
      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), 60000);
      try {
        const res = await fetch('/api/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message: text }),
          credentials: 'include',
          signal: controller.signal,
        });
        const data = await res.json();
        return { ok: res.ok, status: res.status, data };
      } finally {
        clearTimeout(timeout);
      }
    },

    async _callChat(text) {
      this.loading = true;
      const MAX_RETRIES = 3;
      let lastErr = null;
      for (let attempt = 1; attempt <= MAX_RETRIES; attempt++) {
        try {
          const { ok, status, data } = await this._fetchChat(text);
          if (!ok) {
            const errText = data?.text || `Ủa có lỗi xảy ra rồi bạn ơi (HTTP ${status}) 😅 Thử lại nha!`;
            this.messages.push({ role: 'assistant', text: errText, structured: null, actions: [], isError: true, retryText: text });
            this.loading = false;
            return;
          }
          this.messages.push({
            role: 'assistant',
            text: data.text || '',
            structured: data.structured || null,
            actions: (data.structured && data.structured.actions) || [],
          });
          if (data.structured?.type === 'handoff') {
            this.handoff = data.structured;
            this.passenger = { name: '', email: '', phone: '' };
            this.errors = {};
            this.selectedPayment = 'zalopay';
            await this.$nextTick();
            setTimeout(() => { this.panel = 'checkout'; }, 600);
          }
          this.loading = false;
          return;
        } catch (err) {
          lastErr = err;
          console.error(`[chat error] attempt ${attempt}/${MAX_RETRIES}`, err);
          if (attempt < MAX_RETRIES) {
            await new Promise(r => setTimeout(r, 1000 * attempt));
          }
        }
      }
      const msg = lastErr?.name === 'AbortError'
        ? 'Ủa mạng hơi lờ đờ rồi bạn ơi 😅 Thử lại một lần nữa nha!'
        : 'Ôi có gì đó sai sai rồi 😬 Bạn nhắn lại giúp mình với nha!';
      this.messages.push({ role: 'assistant', text: msg, structured: null, actions: [], isError: true, retryText: text });
      this.loading = false;
    },

    // ── Checkout ─────────────────────────────────────────────────────────────
    validateForm() {
      const e = {};
      if (!this.passenger.name.trim()) e.name = 'Bạn chưa nhập tên nè 👀';
      if (!this.passenger.email.trim()) {
        e.email = 'Email bỏ trống rồi bạn ơi!';
      } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(this.passenger.email)) {
        e.email = 'Email trông hơi sai sai, kiểm tra lại nha 🙏';
      }
      if (!this.passenger.phone.trim()) e.phone = 'Số điện thoại đâu rồi bạn ơi? 📱';
      this.errors = e;
      return Object.keys(e).length === 0;
    },

    async confirmBooking() {
      if (!this.validateForm()) return;
      this.bookingLoading = true;
      try {
        const res = await fetch('/api/book', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify({
            sku_id: this.handoff.sku_id,
            summary: this.handoff.summary,
            total_price: this.handoff.total_price,
            currency: this.handoff.currency || 'VND',
            passenger: this.passenger,
            payment_method: this.selectedPayment,
          }),
        });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();

        this.bookingRef = data.booking_ref;
        this.confirmedSummary = data.summary;
        this.confirmedPrice = this.formatPrice(data.total_price) + ' VND';
        this.panel = 'confirmed';
      } catch (err) {
        this.showToast('Ôi đặt chỗ bị lỗi rồi 😬 Thử lại xem sao bạn ơi!');
      } finally {
        this.bookingLoading = false;
      }
    },

    viewOrder() {
      this.openHistory(this.bookingRef);
    },

    async openHistory(autoExpandRef = null) {
      this.panel = 'history';
      this.historyLoading = true;
      this.historyError = false;
      this.expandedBooking = null;
      try {
        const res = await fetch('/api/history', { credentials: 'include' });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        this.historyBookings = data.bookings || [];
        if (autoExpandRef) {
          this.expandedBooking = autoExpandRef;
        }
      } catch (err) {
        this.historyError = true;
        this.historyBookings = [];
      } finally {
        this.historyLoading = false;
      }
    },

    toggleBooking(ref) {
      this.expandedBooking = this.expandedBooking === ref ? null : ref;
    },

    // ── Helpers ──────────────────────────────────────────────────────────────
    resetChat() {
      localStorage.removeItem('claw-chat-messages');
      this.messages = [];
      this.input = '';
      this.loading = false;
      this.panel = 'chat';
      this.handoff = {};
      this.passenger = { name: '', email: '', phone: '' };
      this.errors = {};
      this.bookingRef = '';
      this.pushWelcome();
    },

    scrollBottom() {
      const el = document.getElementById('messages');
      if (el) el.scrollTop = el.scrollHeight;
    },

    showToast(msg) {
      this.toast = msg;
      if (this._toastTimer) clearTimeout(this._toastTimer);
      this._toastTimer = setTimeout(() => { this.toast = ''; }, 4000);
    },

    formatPrice(val) {
      if (!val && val !== 0) return '';
      const num = Number(val);
      if (isNaN(num)) return val;
      return num.toLocaleString('vi-VN');
    },

    formatText(text) {
      if (!text) return '';

      const escape = s => s
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;');

      const inlineFormat = s => escape(s)
        .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.+?)\*/g, '<em>$1</em>');

      const lines = text.split('\n');
      const out = [];
      let i = 0;

      while (i < lines.length) {
        const line = lines[i];
        // Detect markdown table: line starts and ends with |
        if (/^\s*\|/.test(line)) {
          // Collect all consecutive table lines
          const tableLines = [];
          while (i < lines.length && /^\s*\|/.test(lines[i])) {
            tableLines.push(lines[i]);
            i++;
          }
          // Separate header, separator, and body rows
          const rows = tableLines.filter(l => !/^\s*\|[\s\-:|]+\|\s*$/.test(l));
          const parseRow = l => l.replace(/^\s*\|/, '').replace(/\|\s*$/, '').split('|').map(c => c.trim());

          let html = '<table class="msg-table">';
          rows.forEach((row, idx) => {
            const cells = parseRow(row);
            const tag = idx === 0 ? 'th' : 'td';
            html += '<tr>' + cells.map(c => `<${tag}>${inlineFormat(c)}</${tag}>`).join('') + '</tr>';
          });
          html += '</table>';
          out.push(html);
        } else {
          out.push(inlineFormat(line));
          i++;
        }
      }

      return out.join('<br/>').replace(/(<br\/>)+(<table)/, '$2').replace(/(<\/table>)(<br\/>)+/, '$1');
    },

    getAccentClass(title) {
      if (!title) return 'accent-default';
      const t = title.toUpperCase();
      if (t.includes('VN ') || t.includes('VIETNAM')) return 'accent-VN';
      if (t.includes('VJ') || t.includes('VIETJET')) return 'accent-VJ';
      if (t.includes('QH') || t.includes('BAMBOO')) return 'accent-QH';
      if (t.includes('BL') || t.includes('PACIFIC')) return 'accent-BL';
      return 'accent-default';
    },

    getVerticalIcon(handoff) {
      if (!handoff || !handoff.summary) return '🎫';
      const s = handoff.summary.toLowerCase();
      if (s.includes('bay') || s.includes('vn ') || s.includes('vj') || s.includes('qh')) return '✈️';
      if (s.includes('xe') || s.includes('bus')) return '🚌';
      if (s.includes('tàu') || s.includes('train')) return '🚂';
      if (s.includes('khách sạn') || s.includes('hotel')) return '🏨';
      if (s.includes('vé') || s.includes('tham quan')) return '🎡';
      return '🎫';
    },
  };
}
