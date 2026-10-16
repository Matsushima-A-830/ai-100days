let oe = [];
const oe_slice = oe.slice;
const g = oe.flat ? (e)=>oe.flat.call(e) : (e)=>oe.concat.apply([], e);
const { push, indexOf } = oe;
const n = {};
const { toString, hasOwnProperty } = n;
const hasOwnProperty_toString = hasOwnProperty.toString;
const a = hasOwnProperty_toString.call(Object);
const support = {};
const v = function(e) {
    return typeof e === "function" && typeof e.nodeType !== "number" && typeof e.item !== "function";
};
const y = function(e) {
    return e != null && e === e.window;
};
const ie_document = ie.document;
const u = {
    type: true,
    src: true,
    nonce: true,
    noModule: true
};
function m(e, t, n) {
    let r;
    let i;
    const o = (n = n || ie_document).createElement("script");
    o.text = e;
    if (t) {
        for(r in u){
            if (i = t[r] || t.getAttribute && t.getAttribute(r)) {
                o.setAttribute(r, i);
            }
        }
    }
    n.head.appendChild(o).parentNode.removeChild(o);
}
function x(e) {
    if (e == null) {
        return `${e}`;
    }
    if (typeof e === "object" || typeof e === "function") {
        return n[toString.call(e)] || "object";
    }
    return typeof e;
}
const jquery = "3.7.1";
const l = /HTML$/i;
const ce = function(e, t) {
    return new ce.fn.init(e, t);
};
function c(e) {
    const t = !!e && "length" in e && e.length;
    const n = x(e);
    return !v(e) && !y(e) && (n === "array" || t === 0 || typeof t === "number" && t > 0 && t - 1 in e);
}
function fe(e, t) {
    return e.nodeName && e.nodeName.toLowerCase() === t.toLowerCase();
}
ce.fn = ce.prototype = {
    jquery,
    constructor: ce,
    length: 0,
    toArray: function() {
        return oe_slice.call(this);
    },
    get: function(e) {
        if (e == null) {
            return oe_slice.call(this);
        }
        if (e < 0) {
            return this[e + this.length];
        }
        return this[e];
    },
    pushStack: function(e) {
        const t = ce.merge(this.constructor(), e);
        t.prevObject = this;
        return t;
    },
    each: function(e) {
        return ce.each(this, e);
    },
    map: function(n) {
        return this.pushStack(ce.map(this, function(e, t) {
            return n.call(e, t, e);
        }));
    },
    slice: function() {
        return this.pushStack(oe_slice.apply(this, arguments));
    },
    first: function() {
        return this.eq(0);
    },
    last: function() {
        return this.eq(-1);
    },
    even: function() {
        return this.pushStack(ce.grep(this, function(e, t) {
            return (t + 1) % 2;
        }));
    },
    odd: function() {
        return this.pushStack(ce.grep(this, function(e, t) {
            return t % 2;
        }));
    },
    eq: function(e) {
        const length = this.length;
        const n = +e + (e < 0 ? length : 0);
        return this.pushStack(n >= 0 && n < length ? [
            this[n]
        ] : []);
    },
    end: function() {
        return this.prevObject || this.constructor();
    },
    push,
    sort: oe.sort,
    splice: oe.splice
};
ce.extend = ce.fn.extend = function() {
    let e;
    let t;
    let n;
    let r;
    let i;
    let o;
    let a = arguments[0] || {};
    let s = 1;
    const arguments_length = arguments.length;
    let l = false;
    if (typeof a === "boolean") {
        l = a;
        a = arguments[s] || {};
        s++;
    }
    if (!(typeof a === "object" || v(a))) {
        a = {};
    }
    if (s === arguments_length) {
        a = this;
        s--;
    }
    for(; s < arguments_length; s++){
        if ((e = arguments[s]) != null) {
            for(t in e){
                r = e[t];
                if (t !== "__proto__" && a !== r) {
                    if (l && r && (ce.isPlainObject(r) || (i = Array.isArray(r)))) {
                        n = a[t];
                        o = i && !Array.isArray(n) ? [] : i || ce.isPlainObject(n) ? n : {};
                        i = false;
                        a[t] = ce.extend(l, o, r);
                    } else if (r !== undefined) {
                        a[t] = r;
                    }
                }
            }
        }
    }
    return a;
};
ce.extend({
    expando: `jQuery${(jquery + Math.random()).replace(/\D/g, "")}`,
    isReady: true,
    error: function(e) {
        throw new Error(e);
    },
    noop: function() {},
    isPlainObject: function(e) {
        let t;
        let n;
        return !(!e || toString.call(e) !== "[object Object]") && (!(t = Object.getPrototypeOf(e)) || typeof (n = hasOwnProperty.call(t, "constructor") && t.constructor) === "function" && hasOwnProperty_toString.call(n) === a);
    },
    isEmptyObject: function(e) {
        let t;
        for(t in e){
            return false;
        }
        return true;
    },
    globalEval: function(e, t, n) {
        m(e, {
            nonce: t && t.nonce
        }, n);
    },
    each: function(e, t) {
        let n;
        let r = 0;
        if (c(e)) {
            for(n = e.length; r < n; r++){
                if (t.call(e[r], r, e[r]) === false) {
                    break;
                }
            }
        } else {
            for(r in e){
                if (t.call(e[r], r, e[r]) === false) {
                    break;
                }
            }
        }
        return e;
    },
    text: function(e) {
        let t;
        let n = "";
        let r = 0;
        const e_nodeType = e.nodeType;
        if (!e_nodeType) {
            while(t = e[r++]){
                n += ce.text(t);
            }
        }
        if (e_nodeType === 1 || e_nodeType === 11) {
            return e.textContent;
        }
        if (e_nodeType === 9) {
            return e.documentElement.textContent;
        }
        if (e_nodeType === 3 || e_nodeType === 4) {
            return e.nodeValue;
        }
        return n;
    },
    makeArray: function(e, t) {
        const n = t || [];
        if (e != null) {
            if (c(Object(e))) {
                ce.merge(n, typeof e === "string" ? [
                    e
                ] : e);
            } else {
                push.call(n, e);
            }
        }
        return n;
    },
    inArray: function(e, t, n) {
        if (t == null) {
            return -1;
        }
        return indexOf.call(t, e, n);
    },
    isXMLDoc: function(e) {
        const t = e && e.namespaceURI;
        const n = e && (e.ownerDocument || e).documentElement;
        return !l.test(t || n && n.nodeName || "HTML");
    },
    merge: function(e, t) {
        for(var n = +t.length, r = 0, i = e.length; r < n; r++){
            e[i++] = t[r];
        }
        e.length = i;
        return e;
    },
    grep: function(e, t, n) {
        const r = [];
        for(let i = 0, o = e.length, a = !n; i < o; i++){
            if (!t(e[i], i) !== a) {
                r.push(e[i]);
            }
        }
        return r;
    },
    map: function(e, t, n) {
        let r;
        let i;
        let o = 0;
        const a = [];
        if (c(e)) {
            for(r = e.length; o < r; o++){
                if ((i = t(e[o], o, n)) != null) {
                    a.push(i);
                }
            }
        } else {
            for(o in e){
                if ((i = t(e[o], o, n)) != null) {
                    a.push(i);
                }
            }
        }
        return g(a);
    },
    guid: 1,
    support
});
if (typeof Symbol === "function") {
    ce.fn[Symbol.iterator] = oe[Symbol.iterator];
}
ce.each("Boolean Number String Function Array Date RegExp Object Error Symbol".split(" "), function(e, t) {
    n[`[object ${t}]`] = t.toLowerCase();
});
const { pop, sort, splice } = oe;
const ge = "[\\x20\\t\\r\\n\\f]";
const ve = new RegExp(`^${ge}+|((?:^|[^\\\\])(?:\\\\.)*)${ge}+\$`, "g");
ce.contains = function(e, t) {
    const n = t && t.parentNode;
    return e === n || !(!n || n.nodeType !== 1 || !(e.contains ? e.contains(n) : e.compareDocumentPosition && 16 & e.compareDocumentPosition(n)));
};
const f = /([\0-\x1f\x7f]|^-?\d)|^-$|[^\x80-\uFFFF\w-]/g;
function p(e, t) {
    if (t) {
        if (e === "\0") {
            return "\ufffd";
        }
        return `${e.slice(0, -1)}\\${e.charCodeAt(e.length - 1).toString(16)} `;
    }
    return `\\${e}`;
}
ce.escapeSelector = function(e) {
    return `${e}`.replace(f, p);
};
const ye = ie_document;
const me = push;
(()=>{
    let e;
    let b;
    let w;
    let o;
    let a;
    let T;
    let r;
    let C;
    let d;
    let i;
    let k = me;
    const ce_expando = ce.expando;
    let E = 0;
    let n = 0;
    const s = W();
    const c = W();
    const u = W();
    const h = W();
    let l = function(e, t) {
        if (e === t) {
            a = true;
        }
        return 0;
    };
    const f = "checked|selected|async|autofocus|autoplay|controls|defer|disabled|hidden|ismap|loop|multiple|open|readonly|required|scoped";
    const t = `(?:\\\\[\\da-fA-F]{1,6}${ge}?|\\\\[^\\r\\n\\f]|[\\w-]|[^ -\\x7f])+`;
    const p = `\\[${ge}*(${t})(?:${ge}*([*^\$|!~]?=)${ge}*(?:'((?:\\\\.|[^\\\\'])*)'|"((?:\\\\.|[^\\\\"])*)"|(${t}))|)${ge}*\\]`;
    const g = `:(${t})(?:\\((('((?:\\\\.|[^\\\\'])*)'|"((?:\\\\.|[^\\\\"])*)")|((?:\\\\.|[^\\\\()[\\]]|${p})*)|.*)\\)|)`;
    const v = new RegExp(`${ge}+`, "g");
    const y = new RegExp(`^${ge}*,${ge}*`);
    const m = new RegExp(`^${ge}*([>+~]|${ge})${ge}*`);
    const x = new RegExp(`${ge}|>`);
    const j = new RegExp(g);
    const A = new RegExp(`^${t}\$`);
    const match = {
        ID: new RegExp(`^#(${t})`),
        CLASS: new RegExp(`^\\.(${t})`),
        TAG: new RegExp(`^(${t}|[*])`),
        ATTR: new RegExp(`^${p}`),
        PSEUDO: new RegExp(`^${g}`),
        CHILD: new RegExp(`^:(only|first|last|nth|nth-last)-(child|of-type)(?:\\(${ge}*(even|odd|(([+-]|)(\\d*)n|)${ge}*(?:([+-]|)${ge}*(\\d+)|))${ge}*\\)|)`, "i"),
        bool: new RegExp(`^(?:${f})\$`, "i"),
        needsContext: new RegExp(`^${ge}*[>+~]|:(even|odd|eq|gt|lt|nth|first|last)(?:\\(${ge}*((?:-\\d)?\\d*)${ge}*\\)|)(?=[^-]|\$)`, "i")
    };
    const N = /^(?:input|select|textarea|button)$/i;
    const q = /^h\d$/i;
    const L = /^(?:#([\w-]+)|(\w+)|\.([\w-]+))$/;
    const H = /[+~]/;
    const O = new RegExp(`\\\\[\\da-fA-F]{1,6}${ge}?|\\\\([^\\r\\n\\f])`, "g");
    const P = function(e, t) {
        const n = `0x${e.slice(1)}` - 65536;
        return t || (n < 0 ? String.fromCharCode(n + 65536) : String.fromCharCode(n >> 10 | 55296, 1023 & n | 56320));
    };
    var M = function() {
        V();
    };
    const R = J((e)=>e.disabled === true && fe(e, "fieldset"), {
        dir: "parentNode",
        next: "legend"
    });
    try {
        k.apply(oe = oe_slice.call(ye.childNodes), ye.childNodes);
        oe[ye.childNodes.length].nodeType;
    } catch (e) {
        k = {
            apply: function(e, t) {
                me.apply(e, oe_slice.call(t));
            },
            call: function(e) {
                me.apply(e, oe_slice.call(arguments, 1));
            }
        };
    }
    function I(t, e, n, r) {
        let i;
        let o;
        let a;
        let s;
        let u;
        let l;
        let c;
        let f = e && e.ownerDocument;
        const p = e ? e.nodeType : 9;
        n = n || [];
        if (typeof t !== "string" || !t || p !== 1 && p !== 9 && p !== 11) {
            return n;
        }
        if (!r && (V(e), e = e || T, C)) {
            if (p !== 11 && (u = L.exec(t))) {
                if (i = u[1]) {
                    if (p === 9) {
                        if (!(a = e.getElementById(i))) {
                            return n;
                        }
                        if (a.id === i) {
                            k.call(n, a);
                            return n;
                        }
                    } else if (f && (a = f.getElementById(i)) && I.contains(e, a) && a.id === i) {
                        k.call(n, a);
                        return n;
                    }
                } else {
                    if (u[2]) {
                        k.apply(n, e.getElementsByTagName(t));
                        return n;
                    }
                    if ((i = u[3]) && e.getElementsByClassName) {
                        k.apply(n, e.getElementsByClassName(i));
                        return n;
                    }
                }
            }
            if (!(h[`${t} `] || d && d.test(t))) {
                c = t;
                f = e;
                if (p === 1 && (x.test(t) || m.test(t))) {
                    if (!((f = H.test(t) && U(e.parentNode) || e) == e && support.scope)) {
                        if (s = e.getAttribute("id")) {
                            s = ce.escapeSelector(s);
                        } else {
                            e.setAttribute("id", s = ce_expando);
                        }
                    }
                    o = (l = Y(t)).length;
                    while(o--){
                        l[o] = `${s ? `#${s}` : ":scope"} ${Q(l[o])}`;
                    }
                    c = l.join(",");
                }
                try {
                    k.apply(n, f.querySelectorAll(c));
                    return n;
                } catch (e) {
                    h(t, true);
                } finally{
                    if (s === ce_expando) {
                        e.removeAttribute("id");
                    }
                }
            }
        }
        return re(t.replace(ve, "$1"), e, n, r);
    }
    function W() {
        const r = [];
        return function e(t, n) {
            if (r.push(`${t} `) > b.cacheLength) {
                delete e[r.shift()];
            }
            return e[`${t} `] = n;
        };
    }
    function createPseudo(e) {
        e[ce_expando] = true;
        return e;
    }
    function $(e) {
        let t = T.createElement("fieldset");
        try {
            return !!e(t);
        } catch (e) {
            return false;
        } finally{
            if (t.parentNode) {
                t.parentNode.removeChild(t);
            }
            t = null;
        }
    }
    function B(t) {
        return function(e) {
            return fe(e, "input") && e.type === t;
        };
    }
    function _(t) {
        return function(e) {
            return (fe(e, "input") || fe(e, "button")) && e.type === t;
        };
    }
    function z(t) {
        return function(e) {
            if ("form" in e) {
                if (e.parentNode && e.disabled === false) {
                    if ("label" in e) {
                        if ("label" in e.parentNode) {
                            return e.parentNode.disabled === t;
                        }
                        return e.disabled === t;
                    }
                    return e.isDisabled === t || e.isDisabled !== !t && R(e) === t;
                }
                return e.disabled === t;
            }
            return "label" in e && e.disabled === t;
        };
    }
    function X(a) {
        return createPseudo(function(o) {
            o = +o;
            return createPseudo(function(e, t) {
                let n;
                const r = a([], e.length, o);
                let r_length = r.length;
                while(r_length--){
                    if (e[n = r[r_length]]) {
                        e[n] = !(t[n] = e[n]);
                    }
                }
            });
        });
    }
    function U(parentNode) {
        return parentNode && typeof parentNode.getElementsByTagName !== "undefined" && parentNode;
    }
    function V(e) {
        let t;
        const n = e ? e.ownerDocument || e : ye;
        if (n != T && n.nodeType === 9 && n.documentElement) {
            r = (T = n).documentElement;
            C = !ce.isXMLDoc(T);
            i = r.matches || r.webkitMatchesSelector || r.msMatchesSelector;
            if (r.msMatchesSelector && ye != T && (t = T.defaultView) && t.top !== t) {
                t.addEventListener("unload", M);
            }
            support.getById = $((e)=>{
                r.appendChild(e).id = ce.expando;
                return !T.getElementsByName || !T.getElementsByName(ce.expando).length;
            });
            support.disconnectedMatch = $((e)=>i.call(e, "*"));
            support.scope = $(()=>T.querySelectorAll(":scope"));
            support.cssHas = $(()=>{
                try {
                    T.querySelector(":has(*,:jqfake)");
                    return false;
                } catch (e) {
                    return true;
                }
            });
            if (support.getById) {
                b.filter.ID = function(e) {
                    const t = e.replace(O, P);
                    return function(e) {
                        return e.getAttribute("id") === t;
                    };
                };
                b.find.ID = function(e, t) {
                    if (typeof t.getElementById !== "undefined" && C) {
                        const n = t.getElementById(e);
                        if (n) {
                            return [
                                n
                            ];
                        }
                        return [];
                    }
                };
            } else {
                b.filter.ID = function(e) {
                    const n = e.replace(O, P);
                    return function(e) {
                        const t = typeof e.getAttributeNode !== "undefined" && e.getAttributeNode("id");
                        return t && t.value === n;
                    };
                };
                b.find.ID = function(e, t) {
                    if (typeof t.getElementById !== "undefined" && C) {
                        let n;
                        let r;
                        let i;
                        let o = t.getElementById(e);
                        if (o) {
                            if ((n = o.getAttributeNode("id")) && n.value === e) {
                                return [
                                    o
                                ];
                            }
                            i = t.getElementsByName(e);
                            r = 0;
                            while(o = i[r++]){
                                if ((n = o.getAttributeNode("id")) && n.value === e) {
                                    return [
                                        o
                                    ];
                                }
                            }
                        }
                        return [];
                    }
                };
            }
            b.find.TAG = function(e, t) {
                if (typeof t.getElementsByTagName !== "undefined") {
                    return t.getElementsByTagName(e);
                }
                return t.querySelectorAll(e);
            };
            b.find.CLASS = function(e, t) {
                if (typeof t.getElementsByClassName !== "undefined" && C) {
                    return t.getElementsByClassName(e);
                }
            };
            d = [];
            $((e)=>{
                let t;
                r.appendChild(e).innerHTML = `<a id='${ce_expando}' href='' disabled='disabled'></a><select id='${ce_expando}-\r\\' disabled='disabled'><option selected=''></option></select>`;
                if (!e.querySelectorAll("[selected]").length) {
                    d.push(`\\[${ge}*(?:value|${f})`);
                }
                if (!e.querySelectorAll(`[id~=${ce_expando}-]`).length) {
                    d.push("~=");
                }
                if (!e.querySelectorAll(`a#${ce_expando}+*`).length) {
                    d.push(".#.+[+~]");
                }
                if (!e.querySelectorAll(":checked").length) {
                    d.push(":checked");
                }
                (t = T.createElement("input")).setAttribute("type", "hidden");
                e.appendChild(t).setAttribute("name", "D");
                r.appendChild(e).disabled = true;
                if (e.querySelectorAll(":disabled").length !== 2) {
                    d.push(":enabled", ":disabled");
                }
                (t = T.createElement("input")).setAttribute("name", "");
                e.appendChild(t);
                if (!e.querySelectorAll("[name='']").length) {
                    d.push(`\\[${ge}*name${ge}*=${ge}*(?:''|"")`);
                }
            });
            if (!support.cssHas) {
                d.push(":has");
            }
            d = d.length && new RegExp(d.join("|"));
            l = function(e, t) {
                if (e === t) {
                    a = true;
                    return 0;
                }
                let n = !e.compareDocumentPosition - !t.compareDocumentPosition;
                return n || (1 & (n = (e.ownerDocument || e) == (t.ownerDocument || t) ? e.compareDocumentPosition(t) : 1) || !support.sortDetached && t.compareDocumentPosition(e) === n ? e === T || e.ownerDocument == ye && I.contains(ye, e) ? -1 : t === T || t.ownerDocument == ye && I.contains(ye, t) ? 1 : o ? indexOf.call(o, e) - indexOf.call(o, t) : 0 : 4 & n ? -1 : 1);
            };
        }
        return T;
    }
    I.matches = function(e, t) {
        return I(e, null, null, t);
    };
    I.matchesSelector = function(e, t) {
        V(e);
        if (C && !h[`${t} `] && (!d || !d.test(t))) {
            try {
                const n = i.call(e, t);
                if (n || support.disconnectedMatch || e.document && e.document.nodeType !== 11) {
                    return n;
                }
            } catch (e) {
                h(t, true);
            }
        }
        return I(t, T, null, [
            e
        ]).length > 0;
    };
    I.contains = function(e, t) {
        if ((e.ownerDocument || e) != T) {
            V(e);
        }
        return ce.contains(e, t);
    };
    I.attr = function(e, t) {
        if ((e.ownerDocument || e) != T) {
            V(e);
        }
        const n = b.attrHandle[t.toLowerCase()];
        const r = n && hasOwnProperty.call(b.attrHandle, t.toLowerCase()) ? n(e, t, !C) : undefined;
        if (r !== undefined) {
            return r;
        }
        return e.getAttribute(t);
    };
    I.error = function(e) {
        throw new Error(`Syntax error, unrecognized expression: ${e}`);
    };
    ce.uniqueSort = function(e) {
        let t;
        const n = [];
        let r = 0;
        let i = 0;
        a = !support.sortStable;
        o = !support.sortStable && oe_slice.call(e, 0);
        sort.call(e, l);
        if (a) {
            while(t = e[i++]){
                if (t === e[i]) {
                    r = n.push(i);
                }
            }
            while(r--){
                splice.call(e, n[r], 1);
            }
        }
        o = null;
        return e;
    };
    ce.fn.uniqueSort = function() {
        return this.pushStack(ce.uniqueSort(oe_slice.apply(this)));
    };
    (b = ce.expr = {
        cacheLength: 50,
        createPseudo,
        match,
        attrHandle: {},
        find: {},
        relative: {
            ">": {
                dir: "parentNode",
                first: true
            },
            " ": {
                dir: "parentNode"
            },
            "+": {
                dir: "previousSibling",
                first: true
            },
            "~": {
                dir: "previousSibling"
            }
        },
        preFilter: {
            ATTR: function(e) {
                e[1] = e[1].replace(O, P);
                e[3] = (e[3] || e[4] || e[5] || "").replace(O, P);
                if (e[2] === "~=") {
                    e[3] = ` ${e[3]} `;
                }
                return e.slice(0, 4);
            },
            CHILD: function(e) {
                e[1] = e[1].toLowerCase();
                if (e[1].slice(0, 3) === "nth") {
                    if (!e[3]) {
                        I.error(e[0]);
                    }
                    e[4] = +(e[4] ? e[5] + (e[6] || 1) : 2 * (e[3] === "even" || e[3] === "odd"));
                    e[5] = +(e[7] + e[8] || e[3] === "odd");
                } else if (e[3]) {
                    I.error(e[0]);
                }
                return e;
            },
            PSEUDO: function(e) {
                let t;
                const n = !e[6] && e[2];
                if (match.CHILD.test(e[0])) {
                    return null;
                }
                if (e[3]) {
                    e[2] = e[4] || e[5] || "";
                } else if (n && j.test(n) && (t = Y(n, true)) && (t = n.indexOf(")", n.length - t) - n.length)) {
                    e[0] = e[0].slice(0, t);
                    e[2] = n.slice(0, t);
                }
                return e.slice(0, 3);
            }
        },
        filter: {
            TAG: function(e) {
                const t = e.replace(O, P).toLowerCase();
                if (e === "*") {
                    return function() {
                        return true;
                    };
                }
                return function(e) {
                    return fe(e, t);
                };
            },
            CLASS: function(e) {
                let t = s[`${e} `];
                return t || (t = new RegExp(`(^|${ge})${e}(${ge}|\$)`)) && s(e, function(e) {
                    return t.test(typeof e.className === "string" && e.className || typeof e.getAttribute !== "undefined" && e.getAttribute("class") || "");
                });
            },
            ATTR: function(n, r, i) {
                return function(e) {
                    let t = I.attr(e, n);
                    if (t == null) {
                        return r === "!=";
                    }
                    return !r || (t += "", r === "=" ? t === i : r === "!=" ? t !== i : r === "^=" ? i && t.indexOf(i) === 0 : r === "*=" ? i && t.indexOf(i) > -1 : r === "$=" ? i && t.slice(-i.length) === i : r === "~=" ? ` ${t.replace(v, " ")} `.indexOf(i) > -1 : r === "|=" && (t === i || t.slice(0, i.length + 1) === `${i}-`));
                };
            },
            CHILD: function(d, e, t, h, g) {
                const v = d.slice(0, 3) !== "nth";
                const y = d.slice(-4) !== "last";
                const m = e === "of-type";
                if (h === 1 && g === 0) {
                    return function(e) {
                        return !!e.parentNode;
                    };
                }
                return function(e, t, n) {
                    let r;
                    let i;
                    let o;
                    let a;
                    let s;
                    let u = v !== y ? "nextSibling" : "previousSibling";
                    const e_parentNode = e.parentNode;
                    const c = m && e.nodeName.toLowerCase();
                    const f = !n && !m;
                    let p = false;
                    if (e_parentNode) {
                        if (v) {
                            while(u){
                                o = e;
                                while(o = o[u]){
                                    if (m ? fe(o, c) : o.nodeType === 1) {
                                        return false;
                                    }
                                }
                                s = u = d === "only" && !s && "nextSibling";
                            }
                            return true;
                        }
                        s = [
                            y ? e_parentNode.firstChild : e_parentNode.lastChild
                        ];
                        if (y && f) {
                            p = (a = (r = (i = e_parentNode[ce_expando] || (e_parentNode[ce_expando] = {}))[d] || [])[0] === E && r[1]) && r[2];
                            o = a && e_parentNode.childNodes[a];
                            while(o = ++a && o && o[u] || (p = a = 0) || s.pop()){
                                if (o.nodeType === 1 && ++p && o === e) {
                                    i[d] = [
                                        E,
                                        a,
                                        p
                                    ];
                                    break;
                                }
                            }
                        } else {
                            if (f) {
                                p = a = (r = (i = e[ce_expando] || (e[ce_expando] = {}))[d] || [])[0] === E && r[1];
                            }
                            if (p === false) {
                                while(o = ++a && o && o[u] || (p = a = 0) || s.pop()){
                                    if ((m ? fe(o, c) : o.nodeType === 1) && ++p && (f && ((i = o[ce_expando] || (o[ce_expando] = {}))[d] = [
                                        E,
                                        p
                                    ]), o === e)) {
                                        break;
                                    }
                                }
                            }
                        }
                        return (p -= g) === h || p % h == 0 && p / h >= 0;
                    }
                };
            },
            PSEUDO: function(e, o) {
                let t;
                const a = b.pseudos[e] || b.setFilters[e.toLowerCase()] || I.error(`unsupported pseudo: ${e}`);
                if (a[ce_expando]) {
                    return a(o);
                }
                if (a.length > 1) {
                    t = [
                        e,
                        e,
                        "",
                        o
                    ];
                    if (b.setFilters.hasOwnProperty(e.toLowerCase())) {
                        return createPseudo(function(e, t) {
                            let n;
                            const r = a(e, o);
                            let r_length = r.length;
                            while(r_length--){
                                e[n = indexOf.call(e, r[r_length])] = !(t[n] = r[r_length]);
                            }
                        });
                    }
                    return function(e) {
                        return a(e, 0, t);
                    };
                }
                return a;
            }
        },
        pseudos: {
            not: createPseudo(function(e) {
                const r = [];
                const i = [];
                const s = ne(e.replace(ve, "$1"));
                if (s[ce_expando]) {
                    return createPseudo(function(e, t, n, r) {
                        let i;
                        const o = s(e, null, r, []);
                        let e_length = e.length;
                        while(e_length--){
                            if (i = o[e_length]) {
                                e[e_length] = !(t[e_length] = i);
                            }
                        }
                    });
                }
                return function(e, t, n) {
                    r[0] = e;
                    s(r, null, n, i);
                    r[0] = null;
                    return !i.pop();
                };
            }),
            has: createPseudo(function(t) {
                return function(e) {
                    return I(t, e).length > 0;
                };
            }),
            contains: createPseudo(function(t) {
                t = t.replace(O, P);
                return function(e) {
                    return (e.textContent || ce.text(e)).indexOf(t) > -1;
                };
            }),
            lang: createPseudo(function(n) {
                if (!A.test(n || "")) {
                    I.error(`unsupported lang: ${n}`);
                }
                n = n.replace(O, P).toLowerCase();
                return function(e) {
                    let t;
                    do {
                        if (t = C ? e.lang : e.getAttribute("xml:lang") || e.getAttribute("lang")) {
                            return (t = t.toLowerCase()) === n || t.indexOf(`${n}-`) === 0;
                        }
                    }while ((e = e.parentNode) && e.nodeType === 1)
                    return false;
                };
            }),
            target: function(e) {
                const t = ie.location && ie.location.hash;
                return t && t.slice(1) === e.id;
            },
            root: function(e) {
                return e === r;
            },
            focus: function(e) {
                return e === (()=>{
                    try {
                        return T.activeElement;
                    } catch (e) {}
                })() && T.hasFocus() && !!(e.type || e.href || ~e.tabIndex);
            },
            enabled: z(false),
            disabled: z(true),
            checked: function(e) {
                return fe(e, "input") && !!e.checked || fe(e, "option") && !!e.selected;
            },
            selected: function(e) {
                e.parentNode && e.parentNode.selectedIndex;
                return e.selected === true;
            },
            empty: function(e) {
                for(e = e.firstChild; e; e = e.nextSibling){
                    if (e.nodeType < 6) {
                        return false;
                    }
                }
                return true;
            },
            parent: function(e) {
                return !b.pseudos.empty(e);
            },
            header: function(e) {
                return q.test(e.nodeName);
            },
            input: function(e) {
                return N.test(e.nodeName);
            },
            button: function(e) {
                return fe(e, "input") && e.type === "button" || fe(e, "button");
            },
            text: function(e) {
                let t;
                return fe(e, "input") && e.type === "text" && ((t = e.getAttribute("type")) == null || t.toLowerCase() === "text");
            },
            first: X(()=>[
                    0
                ]),
            last: X((e, t)=>[
                    t - 1
                ]),
            eq: X((e, t, n)=>[
                    n < 0 ? n + t : n
                ]),
            even: X((e, t)=>{
                for(let n = 0; n < t; n += 2){
                    e.push(n);
                }
                return e;
            }),
            odd: X((e, t)=>{
                for(let n = 1; n < t; n += 2){
                    e.push(n);
                }
                return e;
            }),
            lt: X((e, t, n)=>{
                let r;
                for(r = n < 0 ? n + t : t < n ? t : n; --r >= 0;){
                    e.push(r);
                }
                return e;
            }),
            gt: X((e, t, n)=>{
                for(let r = n < 0 ? n + t : n; ++r < t;){
                    e.push(r);
                }
                return e;
            })
        }
    }).pseudos.nth = b.pseudos.eq;
    for(e in {
        radio: true,
        checkbox: true,
        file: true,
        password: true,
        image: true
    }){
        b.pseudos[e] = B(e);
    }
    for(e in {
        submit: true,
        reset: true
    }){
        b.pseudos[e] = _(e);
    }
    function G() {}
    function Y(e, t) {
        let n;
        let matches;
        let i;
        let o;
        let a;
        let s;
        let u;
        const l = c[`${e} `];
        if (l) {
            if (t) {
                return 0;
            }
            return l.slice(0);
        }
        a = e;
        s = [];
        u = b.preFilter;
        while(a){
            if (!(n && !(matches = y.exec(a)))) {
                if (matches) {
                    a = a.slice(matches[0].length) || a;
                }
                s.push(i = []);
            }
            n = false;
            if (matches = m.exec(a)) {
                n = matches.shift();
                i.push({
                    value: n,
                    type: matches[0].replace(ve, " ")
                });
                a = a.slice(n.length);
            }
            for(o in b.filter){
                if (!(!(matches = match[o].exec(a)) || u[o] && !(matches = u[o](matches)))) {
                    n = matches.shift();
                    i.push({
                        value: n,
                        type: o,
                        matches
                    });
                    a = a.slice(n.length);
                }
            }
            if (!n) {
                break;
            }
        }
        if (t) {
            return a.length;
        }
        if (a) {
            return I.error(e);
        }
        return c(e, s).slice(0);
    }
    function Q(e) {
        for(var t = 0, n = e.length, r = ""; t < n; t++){
            r += e[t].value;
        }
        return r;
    }
    function J(a, e, t) {
        const { dir, next } = e;
        const l = next || dir;
        const c = t && l === "parentNode";
        const f = n++;
        if (e.first) {
            return function(e, t, n) {
                while(e = e[dir]){
                    if (e.nodeType === 1 || c) {
                        return a(e, t, n);
                    }
                }
                return false;
            };
        }
        return function(e, t, n) {
            let r;
            let i;
            const o = [
                E,
                f
            ];
            if (n) {
                while(e = e[dir]){
                    if ((e.nodeType === 1 || c) && a(e, t, n)) {
                        return true;
                    }
                }
            } else {
                while(e = e[dir]){
                    if (e.nodeType === 1 || c) {
                        i = e[ce_expando] || (e[ce_expando] = {});
                        if (next && fe(e, next)) {
                            e = e[dir] || e;
                        } else {
                            if ((r = i[l]) && r[0] === E && r[1] === f) {
                                return o[2] = r[2];
                            }
                            if ((i[l] = o)[2] = a(e, t, n)) {
                                return true;
                            }
                        }
                    }
                }
            }
            return false;
        };
    }
    function K(i) {
        if (i.length > 1) {
            return function(e, t, n) {
                let i_length = i.length;
                while(i_length--){
                    if (!i[i_length](e, t, n)) {
                        return false;
                    }
                }
                return true;
            };
        }
        return i[0];
    }
    function Z(e, t, n, r, i) {
        let o;
        const a = [];
        for(let s = 0, u = e.length, l = t != null; s < u; s++){
            if (o = e[s]) {
                if (!(n && !n(o, r, i))) {
                    a.push(o);
                    if (l) {
                        t.push(s);
                    }
                }
            }
        }
        return a;
    }
    function ee(d, h, g, v, y, e) {
        if (v && !v[ce_expando]) {
            v = ee(v);
        }
        if (y && !y[ce_expando]) {
            y = ee(y, e);
        }
        return createPseudo(function(e, t, n, r) {
            let i;
            let o;
            let a;
            let s;
            const u = [];
            const l = [];
            const t_length = t.length;
            const f = e || ((e, t, n)=>{
                for(let r = 0, i = t.length; r < i; r++){
                    I(e, t[r], n);
                }
                return n;
            })(h || "*", n.nodeType ? [
                n
            ] : n, []);
            const p = !d || !e && h ? f : Z(f, u, d, n, r);
            if (g) {
                g(p, s = y || (e ? d : t_length || v) ? [] : t, n, r);
            } else {
                s = p;
            }
            if (v) {
                i = Z(s, l);
                v(i, [], n, r);
                o = i.length;
                while(o--){
                    if (a = i[o]) {
                        s[l[o]] = !(p[l[o]] = a);
                    }
                }
            }
            if (e) {
                if (y || d) {
                    if (y) {
                        i = [];
                        o = s.length;
                        while(o--){
                            if (a = s[o]) {
                                i.push(p[o] = a);
                            }
                        }
                        y(null, s = [], i, r);
                    }
                    o = s.length;
                    while(o--){
                        if ((a = s[o]) && (i = y ? indexOf.call(e, a) : u[o]) > -1) {
                            e[i] = !(t[i] = a);
                        }
                    }
                }
            } else {
                s = Z(s === t ? s.splice(t_length, s.length) : s);
                if (y) {
                    y(null, t, s, r);
                } else {
                    k.apply(t, s);
                }
            }
        });
    }
    function te(e) {
        let i;
        let t;
        let n;
        for(var r = e.length, o = b.relative[e[0].type], a = o || b.relative[" "], s = o ? 1 : 0, u = J((e)=>e === i, a, true), l = J((e)=>indexOf.call(i, e) > -1, a, true), c = [
            function(e, t, n) {
                const r = !o && (n || t != w) || ((i = t).nodeType ? u(e, t, n) : l(e, t, n));
                i = null;
                return r;
            }
        ]; s < r; s++){
            if (t = b.relative[e[s].type]) {
                c = [
                    J(K(c), t)
                ];
            } else {
                if ((t = b.filter[e[s].type].apply(null, e[s].matches))[ce_expando]) {
                    for(n = ++s; n < r; n++){
                        if (b.relative[e[n].type]) {
                            break;
                        }
                    }
                    return ee(s > 1 && K(c), s > 1 && Q(e.slice(0, s - 1).concat({
                        value: e[s - 2].type === " " ? "*" : ""
                    })).replace(ve, "$1"), t, s < n && te(e.slice(s, n)), n < r && te(e = e.slice(n)), n < r && Q(e));
                }
                c.push(t);
            }
        }
        return K(c);
    }
    function ne(e, t) {
        let n;
        let v;
        let y;
        let m;
        let x;
        let r;
        const i = [];
        const o = [];
        let a = u[`${e} `];
        if (!a) {
            if (!t) {
                t = Y(e);
            }
            n = t.length;
            while(n--){
                if ((a = te(t[n]))[ce_expando]) {
                    i.push(a);
                } else {
                    o.push(a);
                }
            }
            a = u(e, (v = o, m = (y = i).length > 0, x = v.length > 0, r = function(e, t, n, r, i) {
                let o;
                let a;
                let s;
                let u = 0;
                let l = "0";
                const c = e && [];
                let f = [];
                const p = w;
                const d = e || x && b.find.TAG("*", i);
                const h = E += p == null ? 1 : Math.random() || 0.1;
                const d_length = d.length;
                for(i && (w = t == T || t || i); l !== d_length && (o = d[l]) != null; l++){
                    if (x && o) {
                        a = 0;
                        if (!(t || o.ownerDocument == T)) {
                            V(o);
                            n = !C;
                        }
                        while(s = v[a++]){
                            if (s(o, t || T, n)) {
                                k.call(r, o);
                                break;
                            }
                        }
                        if (i) {
                            E = h;
                        }
                    }
                    if (m) {
                        if (o = !s && o) {
                            u--;
                        }
                        if (e) {
                            c.push(o);
                        }
                    }
                }
                u += l;
                if (m && l !== u) {
                    a = 0;
                    while(s = y[a++]){
                        s(c, f, t, n);
                    }
                    if (e) {
                        if (u > 0) {
                            while(l--){
                                if (!(c[l] || f[l])) {
                                    f[l] = pop.call(r);
                                }
                            }
                        }
                        f = Z(f);
                    }
                    k.apply(r, f);
                    if (i && !e && f.length > 0 && u + y.length > 1) {
                        ce.uniqueSort(r);
                    }
                }
                if (i) {
                    E = h;
                    w = p;
                }
                return c;
            }, m ? createPseudo(r) : r));
            a.selector = e;
        }
        return a;
    }
    function re(e, t, n, r) {
        let i;
        let o;
        let a;
        let s;
        let u;
        const l = typeof e === "function" && e;
        const c = !r && Y(e = l.selector || e);
        n = n || [];
        if (c.length === 1) {
            if ((o = c[0] = c[0].slice(0)).length > 2 && (a = o[0]).type === "ID" && t.nodeType === 9 && C && b.relative[o[1].type]) {
                if (!(t = (b.find.ID(a.matches[0].replace(O, P), t) || [])[0])) {
                    return n;
                }
                if (l) {
                    t = t.parentNode;
                }
                e = e.slice(o.shift().value.length);
            }
            i = match.needsContext.test(e) ? 0 : o.length;
            while(i--){
                a = o[i];
                if (b.relative[s = a.type]) {
                    break;
                }
                if ((u = b.find[s]) && (r = u(a.matches[0].replace(O, P), H.test(o[0].type) && U(t.parentNode) || t))) {
                    o.splice(i, 1);
                    if (!(e = r.length && Q(o))) {
                        k.apply(n, r);
                        return n;
                    }
                    break;
                }
            }
        }
        (l || ne(e, c))(r, t, !C, n, !t || H.test(e) && U(t.parentNode) || t);
        return n;
    }
    G.prototype = b.filters = b.pseudos;
    b.setFilters = new G;
    support.sortStable = ce_expando.split("").sort(l).join("") === ce_expando;
    V();
    support.sortDetached = $((e)=>1 & e.compareDocumentPosition(T.createElement("fieldset")));
    ce.find = I;
    ce.expr[":"] = ce.expr.pseudos;
    ce.unique = ce.uniqueSort;
    I.compile = ne;
    I.select = re;
    I.setDocument = V;
    I.tokenize = Y;
    I.escape = ce.escapeSelector;
    I.getText = ce.text;
    I.isXML = ce.isXMLDoc;
    I.selectors = ce.expr;
    I.support = ce.support;
    I.uniqueSort = ce.uniqueSort;
})();
const d = (e, t, n)=>{
    const r = [];
    const i = n !== undefined;
    while((e = e[t]) && e.nodeType !== 9){
        if (e.nodeType === 1) {
            if (i && ce(e).is(n)) {
                break;
            }
            r.push(e);
        }
    }
    return r;
};
const h = (e, t)=>{
    const n = [];
    for(; e; e = e.nextSibling){
        if (e.nodeType === 1 && e !== t) {
            n.push(e);
        }
    }
    return n;
};
const needsContext = ce.expr.match.needsContext;
const w = /^<([a-z][^\/\0>:\x20\t\r\n\f]*)[\x20\t\r\n\f]*\/?>(?:<\/\1>|)$/i;
function T(e, n, r) {
    if (v(n)) {
        return ce.grep(e, function(e, t) {
            return !!n.call(e, t, e) !== r;
        });
    }
    if (n.nodeType) {
        return ce.grep(e, function(e) {
            return e === n !== r;
        });
    }
    if (typeof n !== "string") {
        return ce.grep(e, function(e) {
            return indexOf.call(n, e) > -1 !== r;
        });
    }
    return ce.filter(n, e, r);
}
ce.filter = function(e, t, n) {
    const r = t[0];
    if (n) {
        e = `:not(${e})`;
    }
    if (t.length === 1 && r.nodeType === 1) {
        if (ce.find.matchesSelector(r, e)) {
            return [
                r
            ];
        }
        return [];
    }
    return ce.find.matches(e, ce.grep(t, function(e) {
        return e.nodeType === 1;
    }));
};
ce.fn.extend({
    find: function(e) {
        let t;
        let n;
        const length = this.length;
        const i = this;
        if (typeof e !== "string") {
            return this.pushStack(ce(e).filter(function() {
                for(t = 0; t < length; t++){
                    if (ce.contains(i[t], this)) {
                        return true;
                    }
                }
            }));
        }
        n = this.pushStack([]);
        for(t = 0; t < length; t++){
            ce.find(e, i[t], n);
        }
        if (length > 1) {
            return ce.uniqueSort(n);
        }
        return n;
    },
    filter: function(e) {
        return this.pushStack(T(this, e || [], false));
    },
    not: function(e) {
        return this.pushStack(T(this, e || [], true));
    },
    is: function(e) {
        return !!T(this, typeof e === "string" && needsContext.test(e) ? ce(e) : e || [], false).length;
    }
});
let k;
const S = /^(?:\s*(<[\w\W]+>)[^>]*|#([\w-]+))$/;
(ce.fn.init = function(e, t, n) {
    let r;
    let i;
    if (!e) {
        return this;
    }
    n = n || k;
    if (typeof e === "string") {
        if (!(r = e[0] === "<" && e[e.length - 1] === ">" && e.length >= 3 ? [
            null,
            e,
            null
        ] : S.exec(e)) || !r[1] && t) {
            if (!t || t.jquery) {
                return (t || n).find(e);
            }
            return this.constructor(t).find(e);
        }
        if (r[1]) {
            t = t instanceof ce ? t[0] : t;
            ce.merge(this, ce.parseHTML(r[1], t && t.nodeType ? t.ownerDocument || t : ie_document, true));
            if (w.test(r[1]) && ce.isPlainObject(t)) {
                for(r in t){
                    if (v(this[r])) {
                        this[r](t[r]);
                    } else {
                        this.attr(r, t[r]);
                    }
                }
            }
            return this;
        }
        if (i = ie_document.getElementById(r[2])) {
            this[0] = i;
            this.length = 1;
        }
        return this;
    }
    if (e.nodeType) {
        this[0] = e;
        this.length = 1;
        return this;
    }
    if (v(e)) {
        if (n.ready !== undefined) {
            return n.ready(e);
        }
        return e(ce);
    }
    return ce.makeArray(e, this);
}).prototype = ce.fn;
k = ce(ie_document);
const E = /^(?:parents|prev(?:Until|All))/;
const j = {
    children: true,
    contents: true,
    next: true,
    prev: true
};
function A(e, t) {
    while((e = e[t]) && e.nodeType !== 1);
    return e;
}
ce.fn.extend({
    has: function(e) {
        const t = ce(e, this);
        const t_length = t.length;
        return this.filter(function() {
            for(let e = 0; e < t_length; e++){
                if (ce.contains(this, t[e])) {
                    return true;
                }
            }
        });
    },
    closest: function(e, t) {
        let n;
        let r = 0;
        const length = this.length;
        const o = [];
        const a = typeof e !== "string" && ce(e);
        if (!needsContext.test(e)) {
            for(; r < length; r++){
                for(n = this[r]; n && n !== t; n = n.parentNode){
                    if (n.nodeType < 11 && (a ? a.index(n) > -1 : n.nodeType === 1 && ce.find.matchesSelector(n, e))) {
                        o.push(n);
                        break;
                    }
                }
            }
        }
        return this.pushStack(o.length > 1 ? ce.uniqueSort(o) : o);
    },
    index: function(e) {
        if (e) {
            if (typeof e === "string") {
                return indexOf.call(ce(e), this[0]);
            }
            return indexOf.call(this, e.jquery ? e[0] : e);
        }
        if (this[0] && this[0].parentNode) {
            return this.first().prevAll().length;
        }
        return -1;
    },
    add: function(e, t) {
        return this.pushStack(ce.uniqueSort(ce.merge(this.get(), ce(e, t))));
    },
    addBack: function(e) {
        return this.add(e == null ? this.prevObject : this.prevObject.filter(e));
    }
});
ce.each({
    parent: function({ parentNode }) {
        if (parentNode && parentNode.nodeType !== 11) {
            return parentNode;
        }
        return null;
    },
    parents: function(e) {
        return d(e, "parentNode");
    },
    parentsUntil: function(e, t, n) {
        return d(e, "parentNode", n);
    },
    next: function(e) {
        return A(e, "nextSibling");
    },
    prev: function(e) {
        return A(e, "previousSibling");
    },
    nextAll: function(e) {
        return d(e, "nextSibling");
    },
    prevAll: function(e) {
        return d(e, "previousSibling");
    },
    nextUntil: function(e, t, n) {
        return d(e, "nextSibling", n);
    },
    prevUntil: function(e, t, n) {
        return d(e, "previousSibling", n);
    },
    siblings: function(e) {
        return h((e.parentNode || {}).firstChild, e);
    },
    children: function(e) {
        return h(e.firstChild);
    },
    contents: function(e) {
        if (e.contentDocument != null && Object.getPrototypeOf(e.contentDocument)) {
            return e.contentDocument;
        }
        if (fe(e, "template")) {
            e = e.content || e;
        }
        return ce.merge([], e.childNodes);
    }
}, function(r, i) {
    ce.fn[r] = function(e, t) {
        let n = ce.map(this, i, e);
        if (r.slice(-5) !== "Until") {
            t = e;
        }
        if (t && typeof t === "string") {
            n = ce.filter(t, n);
        }
        if (this.length > 1) {
            if (!j[r]) {
                ce.uniqueSort(n);
            }
            if (E.test(r)) {
                n.reverse();
            }
        }
        return this.pushStack(n);
    };
});
const D = /[^\x20\t\r\n\f]+/g;
function N(e) {
    return e;
}
function q(e) {
    throw e;
}
function L(e, t, reject, r) {
    let i;
    try {
        if (e && v(i = e.promise)) {
            i.call(e).done(t).fail(reject);
        } else if (e && v(i = e.then)) {
            i.call(e, t, reject);
        } else {
            t(...[
                e
            ].slice(r));
        }
    } catch (error) {
        reject(error);
    }
}
ce.Callbacks = function(r) {
    let e;
    let n;
    r = typeof r === "string" ? (e = r, n = {}, ce.each(e.match(D) || [], function(e, t) {
        n[t] = true;
    }), n) : ce.extend({}, r);
    let i;
    let t;
    let o;
    let a;
    let s = [];
    let u = [];
    let l = -1;
    const c = ()=>{
        a = a || r.once;
        for(o = i = true; u.length; l = -1){
            t = u.shift();
            while(++l < s.length){
                if (s[l].apply(t[0], t[1]) === false && r.stopOnFalse) {
                    l = s.length;
                    t = false;
                }
            }
        }
        if (!r.memory) {
            t = false;
        }
        i = false;
        if (a) {
            s = t ? [] : "";
        }
    };
    var f = {
        add: function() {
            if (s) {
                if (t && !i) {
                    l = s.length - 1;
                    u.push(t);
                }
                (function n(arguments_1) {
                    ce.each(arguments_1, function(e, t) {
                        if (v(t)) {
                            if (!(r.unique && f.has(t))) {
                                s.push(t);
                            }
                        } else if (t && t.length && x(t) !== "string") {
                            n(t);
                        }
                    });
                })(arguments);
                if (t && !i) {
                    c();
                }
            }
            return this;
        },
        remove: function() {
            ce.each(arguments, function(e, t) {
                let n;
                while((n = ce.inArray(t, s, n)) > -1){
                    s.splice(n, 1);
                    if (n <= l) {
                        l--;
                    }
                }
            });
            return this;
        },
        has: function(e) {
            if (e) {
                return ce.inArray(e, s) > -1;
            }
            return s.length > 0;
        },
        empty: function() {
            if (s) {
                s = [];
            }
            return this;
        },
        disable: function() {
            a = u = [];
            t = "";
            s = "";
            return this;
        },
        disabled: function() {
            return !s;
        },
        lock: function() {
            a = u = [];
            if (!(t || i)) {
                t = "";
                s = "";
            }
            return this;
        },
        locked: function() {
            return !!a;
        },
        fireWith: function(e, t) {
            if (!a) {
                t = [
                    e,
                    (t = t || []).slice ? t.slice() : t
                ];
                u.push(t);
                if (!i) {
                    c();
                }
            }
            return this;
        },
        fire: function() {
            f.fireWith(this, arguments);
            return this;
        },
        fired: function() {
            return !!o;
        }
    };
    return f;
};
ce.extend({
    Deferred: function(e) {
        const o = [
            [
                "notify",
                "progress",
                ce.Callbacks("memory"),
                ce.Callbacks("memory"),
                2
            ],
            [
                "resolve",
                "done",
                ce.Callbacks("once memory"),
                ce.Callbacks("once memory"),
                0,
                "resolved"
            ],
            [
                "reject",
                "fail",
                ce.Callbacks("once memory"),
                ce.Callbacks("once memory"),
                1,
                "rejected"
            ]
        ];
        let i = "pending";
        var a = {
            state: function() {
                return i;
            },
            always: function() {
                s.done(arguments).fail(arguments);
                return this;
            },
            catch: function(e) {
                return a.then(null, e);
            },
            pipe: function() {
                let i = arguments;
                return ce.Deferred(function(r) {
                    ce.each(o, function(e, t) {
                        const n = v(i[t[4]]) && i[t[4]];
                        s[t[1]](function() {
                            const e = n && n.apply(this, arguments);
                            if (e && v(e.promise)) {
                                e.promise().progress(r.notify).done(r.resolve).fail(r.reject);
                            } else {
                                r[`${t[0]}With`](this, n ? [
                                    e
                                ] : arguments);
                            }
                        });
                    });
                    i = null;
                }).promise();
            },
            then: function(t, n, r) {
                let u = 0;
                function l(i, o, a, s) {
                    return function() {
                        let n = this;
                        let r = arguments;
                        const e = function() {
                            let e;
                            let t;
                            if (!(i < u)) {
                                if ((e = a.apply(n, r)) === o.promise()) {
                                    throw new TypeError("Thenable self-resolution");
                                }
                                t = e && (typeof e === "object" || typeof e === "function") && e.then;
                                if (v(t)) {
                                    if (s) {
                                        t.call(e, l(u, o, N, s), l(u, o, q, s));
                                    } else {
                                        u++;
                                        t.call(e, l(u, o, N, s), l(u, o, q, s), l(u, o, N, o.notifyWith));
                                    }
                                } else {
                                    if (a !== N) {
                                        n = undefined;
                                        r = [
                                            e
                                        ];
                                    }
                                    (s || o.resolveWith)(n, r);
                                }
                            }
                        };
                        var t = s ? e : function() {
                            try {
                                e();
                            } catch (error) {
                                if (ce.Deferred.exceptionHook) {
                                    ce.Deferred.exceptionHook(error, t.error);
                                }
                                if (u <= i + 1) {
                                    if (a !== q) {
                                        n = undefined;
                                        r = [
                                            error
                                        ];
                                    }
                                    o.rejectWith(n, r);
                                }
                            }
                        };
                        if (i) {
                            t();
                        } else {
                            if (ce.Deferred.getErrorHook) {
                                t.error = ce.Deferred.getErrorHook();
                            } else if (ce.Deferred.getStackHook) {
                                t.error = ce.Deferred.getStackHook();
                            }
                            ie.setTimeout(t);
                        }
                    };
                }
                return ce.Deferred(function(e) {
                    o[0][3].add(l(0, e, v(r) ? r : N, e.notifyWith));
                    o[1][3].add(l(0, e, v(t) ? t : N));
                    o[2][3].add(l(0, e, v(n) ? n : q));
                }).promise();
            },
            promise: function(e) {
                if (e != null) {
                    return ce.extend(e, a);
                }
                return a;
            }
        };
        var s = {};
        ce.each(o, function(e, t) {
            const n = t[2];
            const r = t[5];
            a[t[1]] = n.add;
            if (r) {
                n.add(function() {
                    i = r;
                }, o[3 - e][2].disable, o[3 - e][3].disable, o[0][2].lock, o[0][3].lock);
            }
            n.add(t[3].fire);
            s[t[0]] = function() {
                s[`${t[0]}With`](this === s ? undefined : this, arguments);
                return this;
            };
            s[`${t[0]}With`] = n.fireWith;
        });
        a.promise(s);
        if (e) {
            e.call(s, s);
        }
        return s;
    },
    when: function(e) {
        let arguments_length = arguments.length;
        let t = arguments_length;
        const r = Array(t);
        const i = oe_slice.call(arguments);
        const o = ce.Deferred();
        const a = (t)=>function(e) {
                r[t] = this;
                i[t] = arguments.length > 1 ? oe_slice.call(arguments) : e;
                if (!--arguments_length) {
                    o.resolveWith(r, i);
                }
            };
        if (arguments_length <= 1 && (L(e, o.done(a(t)).resolve, o.reject, !arguments_length), o.state() === "pending" || v(i[t] && i[t].then))) {
            return o.then();
        }
        while(t--){
            L(i[t], a(t), o.reject);
        }
        return o.promise();
    }
});
const H = /^(Eval|Internal|Range|Reference|Syntax|Type|URI)Error$/;
ce.Deferred.exceptionHook = function(e, t) {
    if (ie.console && ie.console.warn && e && H.test(e.name)) {
        ie.console.warn(`jQuery.Deferred exception: ${e.message}`, e.stack, t);
    }
};
ce.readyException = function(e) {
    ie.setTimeout(function() {
        throw e;
    });
};
const O = ce.Deferred();
function P() {
    ie_document.removeEventListener("DOMContentLoaded", P);
    ie.removeEventListener("load", P);
    ce.ready();
}
ce.fn.ready = function(e) {
    O.then(e).catch((e)=>{
        ce.readyException(e);
    });
    return this;
};
ce.extend({
    isReady: false,
    readyWait: 1,
    ready: function(e) {
        if (!((e === true ? --ce.readyWait : ce.isReady) || (ce.isReady = true) !== e && --ce.readyWait > 0)) {
            O.resolveWith(ie_document, [
                ce
            ]);
        }
    }
});
ce.ready.then = O.then;
if (ie_document.readyState === "complete" || ie_document.readyState !== "loading" && !ie_document.documentElement.doScroll) {
    ie.setTimeout(ce.ready);
} else {
    ie_document.addEventListener("DOMContentLoaded", P);
    ie.addEventListener("load", P);
}
const M = (e, t, n, r, i, o, a)=>{
    let s = 0;
    const e_length = e.length;
    let l = n == null;
    if (x(n) === "object") {
        i = true;
        for(s in n){
            M(e, t, s, n[s], true, o, a);
        }
    } else if (r !== undefined && (i = true, v(r) || (a = true), l && (a ? (t.call(e, r), t = null) : (l = t, t = function(e, t, n) {
        return l.call(ce(e), n);
    })), t)) {
        for(; s < e_length; s++){
            t(e[s], n, a ? r : r.call(e[s], s, t(e[s], n)));
        }
    }
    if (i) {
        return e;
    }
    if (l) {
        return t.call(e);
    }
    if (e_length) {
        return t(e[0], n);
    }
    return o;
};
const R = /^-ms-/;
const I = /-([a-z])/g;
function W(e, t) {
    return t.toUpperCase();
}
function F(e) {
    return e.replace(R, "ms-").replace(I, W);
}
const $ = (e)=>e.nodeType === 1 || e.nodeType === 9 || !+e.nodeType;
function B() {
    this.expando = ce.expando + B.uid++;
}
B.uid = 1;
B.prototype = {
    cache: function(e) {
        let t = e[this.expando];
        if (!t) {
            t = {};
            if ($(e)) {
                if (e.nodeType) {
                    e[this.expando] = t;
                } else {
                    Object.defineProperty(e, this.expando, {
                        value: t,
                        configurable: true
                    });
                }
            }
        }
        return t;
    },
    set: function(e, t, n) {
        let r;
        const i = this.cache(e);
        if (typeof t === "string") {
            i[F(t)] = n;
        } else {
            for(r in t){
                i[F(r)] = t[r];
            }
        }
        return i;
    },
    get: function(e, t) {
        if (t === undefined) {
            return this.cache(e);
        }
        return e[this.expando] && e[this.expando][F(t)];
    },
    access: function(e, t, n) {
        if (t === undefined || t && typeof t === "string" && n === undefined) {
            return this.get(e, t);
        }
        this.set(e, t, n);
        if (n !== undefined) {
            return n;
        }
        return t;
    },
    remove: function(e, t) {
        let n;
        const r = e[this.expando];
        if (r !== undefined) {
            if (t !== undefined) {
                n = (t = Array.isArray(t) ? t.map(F) : (t = F(t)) in r ? [
                    t
                ] : t.match(D) || []).length;
                while(n--){
                    delete r[t[n]];
                }
            }
            if (t === undefined || ce.isEmptyObject(r)) {
                if (e.nodeType) {
                    e[this.expando] = undefined;
                } else {
                    delete e[this.expando];
                }
            }
        }
    },
    hasData: function(e) {
        const t = e[this.expando];
        return t !== undefined && !ce.isEmptyObject(t);
    }
};
const _ = new B;
const z = new B;
const X = /^(?:\{[\w\W]*\}|\[[\w\W]*\])$/;
const U = /[A-Z]/g;
function V(e, t, n) {
    let r;
    let i;
    if (n === undefined && e.nodeType === 1) {
        r = `data-${t.replace(U, "-$&").toLowerCase()}`;
        if (typeof (n = e.getAttribute(r)) === "string") {
            try {
                n = (i = n) === "true" || i !== "false" && (i === "null" ? null : i === `${+i}` ? +i : X.test(i) ? JSON.parse(i) : i);
            } catch (e) {}
            z.set(e, t, n);
        } else {
            n = undefined;
        }
    }
    return n;
}
ce.extend({
    hasData: function(e) {
        return z.hasData(e) || _.hasData(e);
    },
    data: function(e, t, n) {
        return z.access(e, t, n);
    },
    removeData: function(e, t) {
        z.remove(e, t);
    },
    _data: function(e, t, n) {
        return _.access(e, t, n);
    },
    _removeData: function(e, t) {
        _.remove(e, t);
    }
});
ce.fn.extend({
    data: function(n, e) {
        let t;
        let r;
        let i;
        const o = this[0];
        const a = o && o.attributes;
        if (n === undefined) {
            if (this.length && (i = z.get(o), o.nodeType === 1 && !_.get(o, "hasDataAttrs"))) {
                t = a.length;
                while(t--){
                    if (a[t] && (r = a[t].name).indexOf("data-") === 0) {
                        r = F(r.slice(5));
                        V(o, r, i[r]);
                    }
                }
                _.set(o, "hasDataAttrs", true);
            }
            return i;
        }
        if (typeof n === "object") {
            return this.each(function() {
                z.set(this, n);
            });
        }
        return M(this, function(e) {
            let t;
            if (o && e === undefined) {
                if ((t = z.get(o, n)) !== undefined) {
                    return t;
                }
                if ((t = V(o, n)) !== undefined) {
                    return t;
                }
                return undefined;
            }
            this.each(function() {
                z.set(this, n, e);
            });
        }, null, e, arguments.length > 1, null, true);
    },
    removeData: function(e) {
        return this.each(function() {
            z.remove(this, e);
        });
    }
});
ce.extend({
    queue: function(e, t, n) {
        let r;
        if (e) {
            t = `${t || "fx"}queue`;
            r = _.get(e, t);
            if (n) {
                if (!r || Array.isArray(n)) {
                    r = _.access(e, t, ce.makeArray(n));
                } else {
                    r.push(n);
                }
            }
            return r || [];
        }
    },
    dequeue: function(e, t) {
        t = t || "fx";
        const n = ce.queue(e, t);
        let n_length = n.length;
        let i = n.shift();
        const o = ce._queueHooks(e, t);
        if (i === "inprogress") {
            i = n.shift();
            n_length--;
        }
        if (i) {
            if (t === "fx") {
                n.unshift("inprogress");
            }
            delete o.stop;
            i.call(e, function() {
                ce.dequeue(e, t);
            }, o);
        }
        if (!n_length && o) {
            o.empty.fire();
        }
    },
    _queueHooks: function(e, t) {
        const n = `${t}queueHooks`;
        return _.get(e, n) || _.access(e, n, {
            empty: ce.Callbacks("once memory").add(function() {
                _.remove(e, [
                    `${t}queue`,
                    n
                ]);
            })
        });
    }
});
ce.fn.extend({
    queue: function(t, n) {
        let e = 2;
        if (typeof t !== "string") {
            n = t;
            t = "fx";
            e--;
        }
        if (arguments.length < e) {
            return ce.queue(this[0], t);
        }
        if (n === undefined) {
            return this;
        }
        return this.each(function() {
            const e = ce.queue(this, t, n);
            ce._queueHooks(this, t);
            if (t === "fx" && e[0] !== "inprogress") {
                ce.dequeue(this, t);
            }
        });
    },
    dequeue: function(e) {
        return this.each(function() {
            ce.dequeue(this, e);
        });
    },
    clearQueue: function(e) {
        return this.queue(e || "fx", []);
    },
    promise: function(e, t) {
        let n;
        let r = 1;
        const i = ce.Deferred();
        const o = this;
        let length = this.length;
        const s = function() {
            if (!--r) {
                i.resolveWith(o, [
                    o
                ]);
            }
        };
        if (typeof e !== "string") {
            t = e;
            e = undefined;
        }
        e = e || "fx";
        while(length--){
            if ((n = _.get(o[length], `${e}queueHooks`)) && n.empty) {
                r++;
                n.empty.add(s);
            }
        }
        s();
        return i.promise(t);
    }
});
const source = /[+-]?(?:\d*\.|)\d+(?:[eE][+-]?\d+|)/.source;
const Y = new RegExp(`^(?:([+-])=|)(${source})([a-z%]*)\$`, "i");
const Q = [
    "Top",
    "Right",
    "Bottom",
    "Left"
];
const C_documentElement = ie_document.documentElement;
let K = function(e) {
    return ce.contains(e.ownerDocument, e);
};
const Z = {
    composed: true
};
if (C_documentElement.getRootNode) {
    K = function(e) {
        return ce.contains(e.ownerDocument, e) || e.getRootNode(Z) === e.ownerDocument;
    };
}
const ee = function(e, t) {
    return (e = t || e).style.display === "none" || e.style.display === "" && K(e) && ce.css(e, "display") === "none";
};
function te(e, t, n, r) {
    let i;
    let o;
    let a = 20;
    const s = r ? ()=>r.cur() : ()=>ce.css(e, t, "");
    let u = s();
    let l = n && n[3] || (ce.cssNumber[t] ? "" : "px");
    let c = e.nodeType && (ce.cssNumber[t] || l !== "px" && +u) && Y.exec(ce.css(e, t));
    if (c && c[3] !== l) {
        u /= 2;
        l = l || c[3];
        c = +u || 1;
        while(a--){
            ce.style(e, t, c + l);
            if ((1 - o) * (1 - (o = s() / u || 0.5)) <= 0) {
                a = 0;
            }
            c /= o;
        }
        c *= 2;
        ce.style(e, t, c + l);
        n = n || [];
    }
    if (n) {
        c = +c || +u || 0;
        i = n[1] ? c + (n[1] + 1) * n[2] : +n[2];
        if (r) {
            r.unit = l;
            r.start = c;
            r.end = i;
        }
    }
    return i;
}
const ne = {};
function re(e, t) {
    let n;
    let r;
    let i;
    let o;
    let a;
    let s;
    let u;
    const l = [];
    for(var c = 0, f = e.length; c < f; c++){
        if ((r = e[c]).style) {
            n = r.style.display;
            if (t) {
                if (n === "none") {
                    l[c] = _.get(r, "display") || null;
                    if (!l[c]) {
                        r.style.display = "";
                    }
                }
                if (r.style.display === "" && ee(r)) {
                    l[c] = (u = a = o = undefined, a = (i = r).ownerDocument, s = i.nodeName, (u = ne[s]) || (o = a.body.appendChild(a.createElement(s)), u = ce.css(o, "display"), o.parentNode.removeChild(o), u === "none" && (u = "block"), ne[s] = u));
                }
            } else if (n !== "none") {
                l[c] = "none";
                _.set(r, "display", n);
            }
        }
    }
    for(c = 0; c < f; c++){
        if (l[c] != null) {
            e[c].style.display = l[c];
        }
    }
    return e;
}
ce.fn.extend({
    show: function() {
        return re(this, true);
    },
    hide: function() {
        return re(this);
    },
    toggle: function(e) {
        if (typeof e === "boolean") {
            if (e) {
                return this.show();
            }
            return this.hide();
        }
        return this.each(function() {
            if (ee(this)) {
                ce(this).show();
            } else {
                ce(this).hide();
            }
        });
    }
});
let xe;
let be;
const we = /^(?:checkbox|radio)$/i;
const Te = /<([a-z][^\/\0>\x20\t\r\n\f]*)/i;
const Ce = /^$|^module$|\/(?:java|ecma)script/i;
xe = ie_document.createDocumentFragment().appendChild(ie_document.createElement("div"));
(be = ie_document.createElement("input")).setAttribute("type", "radio");
be.setAttribute("checked", "checked");
be.setAttribute("name", "t");
xe.appendChild(be);
support.checkClone = xe.cloneNode(true).cloneNode(true).lastChild.checked;
xe.innerHTML = "<textarea>x</textarea>";
support.noCloneChecked = !!xe.cloneNode(true).lastChild.defaultValue;
xe.innerHTML = "<option></option>";
support.option = !!xe.lastChild;
const ke = {
    thead: [
        1,
        "<table>",
        "</table>"
    ],
    col: [
        2,
        "<table><colgroup>",
        "</colgroup></table>"
    ],
    tr: [
        2,
        "<table><tbody>",
        "</tbody></table>"
    ],
    td: [
        3,
        "<table><tbody><tr>",
        "</tr></tbody></table>"
    ],
    _default: [
        0,
        "",
        ""
    ]
};
function Se(e, t) {
    let n;
    n = typeof e.getElementsByTagName !== "undefined" ? e.getElementsByTagName(t || "*") : typeof e.querySelectorAll !== "undefined" ? e.querySelectorAll(t || "*") : [];
    if (t === undefined || t && fe(e, t)) {
        return ce.merge([
            e
        ], n);
    }
    return n;
}
function Ee(e, t) {
    for(let n = 0, r = e.length; n < r; n++){
        _.set(e[n], "globalEval", !t || _.get(t[n], "globalEval"));
    }
}
ke.tbody = ke.tfoot = ke.colgroup = ke.caption = ke.thead;
ke.th = ke.td;
if (!support.option) {
    ke.optgroup = ke.option = [
        1,
        "<select multiple='multiple'>",
        "</select>"
    ];
}
const je = /<|&#?\w+;/;
function Ae(e, t, n, r, i) {
    let o;
    let a;
    let s;
    let u;
    let l;
    let c;
    const f = t.createDocumentFragment();
    const p = [];
    for(var d = 0, h = e.length; d < h; d++){
        if ((o = e[d]) || o === 0) {
            if (x(o) === "object") {
                ce.merge(p, o.nodeType ? [
                    o
                ] : o);
            } else if (je.test(o)) {
                a = a || f.appendChild(t.createElement("div"));
                s = (Te.exec(o) || [
                    "",
                    ""
                ])[1].toLowerCase();
                u = ke[s] || ke._default;
                a.innerHTML = u[1] + ce.htmlPrefilter(o) + u[2];
                c = u[0];
                while(c--){
                    a = a.lastChild;
                }
                ce.merge(p, a.childNodes);
                a = f.firstChild;
                a.textContent = "";
            } else {
                p.push(t.createTextNode(o));
            }
        }
    }
    f.textContent = "";
    d = 0;
    while(o = p[d++]){
        if (r && ce.inArray(o, r) > -1) {
            if (i) {
                i.push(o);
            }
        } else {
            l = K(o);
            a = Se(f.appendChild(o), "script");
            if (l) {
                Ee(a);
            }
            if (n) {
                c = 0;
                while(o = a[c++]){
                    if (Ce.test(o.type || "")) {
                        n.push(o);
                    }
                }
            }
        }
    }
    return f;
}
const De = /^([^.]*)(?:\.(.+)|)/;
function Ne() {
    return true;
}
function qe() {
    return false;
}
function Le(e, t, n, r, i, o) {
    let a;
    let s;
    if (typeof t === "object") {
        if (typeof n !== "string") {
            r = r || n;
            n = undefined;
        }
        for(s in t){
            Le(e, s, n, r, t[s], o);
        }
        return e;
    }
    if (r == null && i == null) {
        i = n;
        n = undefined;
        r = undefined;
    } else {
        if (i == null) {
            if (typeof n === "string") {
                i = r;
                r = undefined;
            } else {
                i = r;
                r = n;
                n = undefined;
            }
        }
    }
    if (i === false) {
        i = qe;
    } else if (!i) {
        return e;
    }
    if (o === 1) {
        a = i;
        i = function(e) {
            ce().off(e);
            return a.apply(this, arguments);
        };
        i.guid = a.guid || (a.guid = ce.guid++);
    }
    return e.each(function() {
        ce.event.add(this, t, i, r, n);
    });
}
function He(e, r, t) {
    if (t) {
        _.set(e, r, false);
        ce.event.add(e, r, {
            namespace: false,
            handler: function(e) {
                let t;
                let n = _.get(this, r);
                if (1 & e.isTrigger && this[r]) {
                    if (n) {
                        if ((ce.event.special[r] || {}).delegateType) {
                            e.stopPropagation();
                        }
                    } else {
                        n = oe_slice.call(arguments);
                        _.set(this, r, n);
                        this[r]();
                        t = _.get(this, r);
                        _.set(this, r, false);
                        if (n !== t) {
                            e.stopImmediatePropagation();
                            e.preventDefault();
                            return t;
                        }
                    }
                } else {
                    if (n) {
                        _.set(this, r, ce.event.trigger(n[0], n.slice(1), this));
                        e.stopPropagation();
                        e.isImmediatePropagationStopped = Ne;
                    }
                }
            }
        });
    } else if (_.get(e, r) === undefined) {
        ce.event.add(e, r, Ne);
    }
}
ce.event = {
    global: {},
    add: function(t, e, handler, r, selector) {
        let o;
        let a;
        let s;
        let u;
        let l;
        let c;
        let f;
        let p;
        let d;
        let h;
        let origType;
        const v = _.get(t);
        if ($(t)) {
            if (handler.handler) {
                handler = (o = handler).handler;
                selector = o.selector;
            }
            if (selector) {
                ce.find.matchesSelector(C_documentElement, selector);
            }
            if (!handler.guid) {
                handler.guid = ce.guid++;
            }
            if (!(u = v.events)) {
                u = v.events = Object.create(null);
            }
            if (!(a = v.handle)) {
                a = v.handle = function(e) {
                    if (typeof ce !== "undefined" && ce.event.triggered !== e.type) {
                        return ce.event.dispatch.apply(t, arguments);
                    }
                };
            }
            l = (e = (e || "").match(D) || [
                ""
            ]).length;
            while(l--){
                d = origType = (s = De.exec(e[l]) || [])[1];
                h = (s[2] || "").split(".").sort();
                if (d) {
                    f = ce.event.special[d] || {};
                    d = (selector ? f.delegateType : f.bindType) || d;
                    f = ce.event.special[d] || {};
                    c = ce.extend({
                        type: d,
                        origType,
                        data: r,
                        handler,
                        guid: handler.guid,
                        selector,
                        needsContext: selector && ce.expr.match.needsContext.test(selector),
                        namespace: h.join(".")
                    }, o);
                    if (!(p = u[d])) {
                        p = u[d] = [];
                        p.delegateCount = 0;
                        if (!(f.setup && f.setup.call(t, r, h, a) !== false)) {
                            if (t.addEventListener) {
                                t.addEventListener(d, a);
                            }
                        }
                    }
                    if (f.add) {
                        f.add.call(t, c);
                        if (!c.handler.guid) {
                            c.handler.guid = handler.guid;
                        }
                    }
                    if (selector) {
                        p.splice(p.delegateCount++, 0, c);
                    } else {
                        p.push(c);
                    }
                    ce.event.global[d] = true;
                }
            }
        }
    },
    remove: function(e, t, n, r, i) {
        let o;
        let a;
        let s;
        let u;
        let l;
        let c;
        let f;
        let p;
        let d;
        let h;
        let g;
        const v = _.hasData(e) && _.get(e);
        if (v && (u = v.events)) {
            l = (t = (t || "").match(D) || [
                ""
            ]).length;
            while(l--){
                d = g = (s = De.exec(t[l]) || [])[1];
                h = (s[2] || "").split(".").sort();
                if (d) {
                    f = ce.event.special[d] || {};
                    p = u[d = (r ? f.delegateType : f.bindType) || d] || [];
                    s = s[2] && new RegExp(`(^|\\.)${h.join("\\.(?:.*\\.|)")}(\\.|\$)`);
                    a = o = p.length;
                    while(o--){
                        c = p[o];
                        if (!(!i && g !== c.origType || n && n.guid !== c.guid || s && !s.test(c.namespace) || r && r !== c.selector && (r !== "**" || !c.selector))) {
                            p.splice(o, 1);
                            if (c.selector) {
                                p.delegateCount--;
                            }
                            if (f.remove) {
                                f.remove.call(e, c);
                            }
                        }
                    }
                    if (a && !p.length) {
                        if (!(f.teardown && f.teardown.call(e, h, v.handle) !== false)) {
                            ce.removeEvent(e, d, v.handle);
                        }
                        delete u[d];
                    }
                } else {
                    for(d in u){
                        ce.event.remove(e, d + t[l], n, r, true);
                    }
                }
            }
            if (ce.isEmptyObject(u)) {
                _.remove(e, "handle events");
            }
        }
    },
    dispatch: function(e) {
        let t;
        let n;
        let r;
        let i;
        let o;
        let a;
        const s = new Array(arguments.length);
        const u = ce.event.fix(e);
        const l = (_.get(this, "events") || Object.create(null))[u.type] || [];
        const c = ce.event.special[u.type] || {};
        s[0] = u;
        for(t = 1; t < arguments.length; t++){
            s[t] = arguments[t];
        }
        u.delegateTarget = this;
        if (!c.preDispatch || c.preDispatch.call(this, u) !== false) {
            a = ce.event.handlers.call(this, u, l);
            t = 0;
            while((i = a[t++]) && !u.isPropagationStopped()){
                u.currentTarget = i.elem;
                n = 0;
                while((o = i.handlers[n++]) && !u.isImmediatePropagationStopped()){
                    if (!(u.rnamespace && o.namespace !== false && !u.rnamespace.test(o.namespace))) {
                        u.handleObj = o;
                        u.data = o.data;
                        if ((r = ((ce.event.special[o.origType] || {}).handle || o.handler).apply(i.elem, s)) !== undefined && (u.result = r) === false) {
                            u.preventDefault();
                            u.stopPropagation();
                        }
                    }
                }
            }
            if (c.postDispatch) {
                c.postDispatch.call(this, u);
            }
            return u.result;
        }
    },
    handlers: function(e, t) {
        let n;
        let r;
        let i;
        let handlers;
        let a;
        const s = [];
        const t_delegateCount = t.delegateCount;
        let e_target = e.target;
        if (t_delegateCount && e_target.nodeType && !(e.type === "click" && e.button >= 1)) {
            for(; e_target !== this; e_target = e_target.parentNode || this){
                if (e_target.nodeType === 1 && (e.type !== "click" || e_target.disabled !== true)) {
                    handlers = [];
                    a = {};
                    for(n = 0; n < t_delegateCount; n++){
                        if (a[i = `${(r = t[n]).selector} `] === undefined) {
                            a[i] = r.needsContext ? ce(i, this).index(e_target) > -1 : ce.find(i, this, null, [
                                e_target
                            ]).length;
                        }
                        if (a[i]) {
                            handlers.push(r);
                        }
                    }
                    if (handlers.length) {
                        s.push({
                            elem: e_target,
                            handlers
                        });
                    }
                }
            }
        }
        e_target = this;
        if (t_delegateCount < t.length) {
            s.push({
                elem: e_target,
                handlers: t.slice(t_delegateCount)
            });
        }
        return s;
    },
    addProp: function(t, e) {
        Object.defineProperty(ce.Event.prototype, t, {
            enumerable: true,
            configurable: true,
            get: v(e) ? function() {
                if (this.originalEvent) {
                    return e(this.originalEvent);
                }
            } : function() {
                if (this.originalEvent) {
                    return this.originalEvent[t];
                }
            },
            set: function(value) {
                Object.defineProperty(this, t, {
                    enumerable: true,
                    configurable: true,
                    writable: true,
                    value
                });
            }
        });
    },
    fix: function(e) {
        if (e[ce.expando]) {
            return e;
        }
        return new ce.Event(e);
    },
    special: {
        load: {
            noBubble: true
        },
        click: {
            setup: function(e) {
                const t = this || e;
                if (we.test(t.type) && t.click && fe(t, "input")) {
                    He(t, "click", true);
                }
                return false;
            },
            trigger: function(e) {
                const t = this || e;
                if (we.test(t.type) && t.click && fe(t, "input")) {
                    He(t, "click");
                }
                return true;
            },
            _default: function({ target }) {
                return we.test(target.type) && target.click && fe(target, "input") && _.get(target, "click") || fe(target, "a");
            }
        },
        beforeunload: {
            postDispatch: function(e) {
                if (e.result !== undefined && e.originalEvent) {
                    e.originalEvent.returnValue = e.result;
                }
            }
        }
    }
};
ce.removeEvent = function(e, t, n) {
    if (e.removeEventListener) {
        e.removeEventListener(t, n);
    }
};
ce.Event = function(e, t) {
    if (!(this instanceof ce.Event)) {
        return new ce.Event(e, t);
    }
    if (e && e.type) {
        this.originalEvent = e;
        this.type = e.type;
        this.isDefaultPrevented = e.defaultPrevented || e.defaultPrevented === undefined && e.returnValue === false ? Ne : qe;
        this.target = e.target && e.target.nodeType === 3 ? e.target.parentNode : e.target;
        this.currentTarget = e.currentTarget;
        this.relatedTarget = e.relatedTarget;
    } else {
        this.type = e;
    }
    if (t) {
        ce.extend(this, t);
    }
    this.timeStamp = e && e.timeStamp || Date.now();
    this[ce.expando] = true;
};
ce.Event.prototype = {
    constructor: ce.Event,
    isDefaultPrevented: qe,
    isPropagationStopped: qe,
    isImmediatePropagationStopped: qe,
    isSimulated: false,
    preventDefault: function() {
        const originalEvent = this.originalEvent;
        this.isDefaultPrevented = Ne;
        if (originalEvent && !this.isSimulated) {
            originalEvent.preventDefault();
        }
    },
    stopPropagation: function() {
        const originalEvent = this.originalEvent;
        this.isPropagationStopped = Ne;
        if (originalEvent && !this.isSimulated) {
            originalEvent.stopPropagation();
        }
    },
    stopImmediatePropagation: function() {
        const originalEvent = this.originalEvent;
        this.isImmediatePropagationStopped = Ne;
        if (originalEvent && !this.isSimulated) {
            originalEvent.stopImmediatePropagation();
        }
        this.stopPropagation();
    }
};
ce.each({
    altKey: true,
    bubbles: true,
    cancelable: true,
    changedTouches: true,
    ctrlKey: true,
    detail: true,
    eventPhase: true,
    metaKey: true,
    pageX: true,
    pageY: true,
    shiftKey: true,
    view: true,
    char: true,
    code: true,
    charCode: true,
    key: true,
    keyCode: true,
    button: true,
    buttons: true,
    clientX: true,
    clientY: true,
    offsetX: true,
    offsetY: true,
    pointerId: true,
    pointerType: true,
    screenX: true,
    screenY: true,
    targetTouches: true,
    toElement: true,
    touches: true,
    which: true
}, ce.event.addProp);
ce.each({
    focus: "focusin",
    blur: "focusout"
}, function(r, delegateType) {
    function o(e) {
        if (ie_document.documentMode) {
            const t = _.get(this, "handle");
            const n = ce.event.fix(e);
            n.type = e.type === "focusin" ? "focus" : "blur";
            n.isSimulated = true;
            t(e);
            if (n.target === n.currentTarget) {
                t(n);
            }
        } else {
            ce.event.simulate(delegateType, e.target, ce.event.fix(e));
        }
    }
    ce.event.special[r] = {
        setup: function() {
            let e;
            He(this, r, true);
            if (!ie_document.documentMode) {
                return false;
            }
            if (!(e = _.get(this, delegateType))) {
                this.addEventListener(delegateType, o);
            }
            _.set(this, delegateType, (e || 0) + 1);
        },
        trigger: function() {
            He(this, r);
            return true;
        },
        teardown: function() {
            let e;
            if (!ie_document.documentMode) {
                return false;
            }
            if (e = _.get(this, delegateType) - 1) {
                _.set(this, delegateType, e);
            } else {
                this.removeEventListener(delegateType, o);
                _.remove(this, delegateType);
            }
        },
        _default: function(e) {
            return _.get(e.target, r);
        },
        delegateType
    };
    ce.event.special[delegateType] = {
        setup: function() {
            const e = this.ownerDocument || this.document || this;
            const t = ie_document.documentMode ? this : e;
            const n = _.get(t, delegateType);
            if (!n) {
                if (ie_document.documentMode) {
                    this.addEventListener(delegateType, o);
                } else {
                    e.addEventListener(r, o, true);
                }
            }
            _.set(t, delegateType, (n || 0) + 1);
        },
        teardown: function() {
            const e = this.ownerDocument || this.document || this;
            const t = ie_document.documentMode ? this : e;
            const n = _.get(t, delegateType) - 1;
            if (n) {
                _.set(t, delegateType, n);
            } else {
                if (ie_document.documentMode) {
                    this.removeEventListener(delegateType, o);
                } else {
                    e.removeEventListener(r, o, true);
                }
                _.remove(t, delegateType);
            }
        }
    };
});
ce.each({
    mouseenter: "mouseover",
    mouseleave: "mouseout",
    pointerenter: "pointerover",
    pointerleave: "pointerout"
}, function(e, i) {
    ce.event.special[e] = {
        delegateType: i,
        bindType: i,
        handle: function(e) {
            let t;
            const { relatedTarget, handleObj } = e;
            if (!(relatedTarget && (relatedTarget === this || ce.contains(this, relatedTarget)))) {
                e.type = handleObj.origType;
                t = handleObj.handler.apply(this, arguments);
                e.type = i;
            }
            return t;
        }
    };
});
ce.fn.extend({
    on: function(e, t, n, r) {
        return Le(this, e, t, n, r);
    },
    one: function(e, t, n, r) {
        return Le(this, e, t, n, r, 1);
    },
    off: function(e, t, n) {
        let r;
        let i;
        if (e && e.preventDefault && e.handleObj) {
            r = e.handleObj;
            ce(e.delegateTarget).off(r.namespace ? `${r.origType}.${r.namespace}` : r.origType, r.selector, r.handler);
            return this;
        }
        if (typeof e === "object") {
            for(i in e){
                this.off(i, t, e[i]);
            }
            return this;
        }
        if (!(t !== false && typeof t !== "function")) {
            n = t;
            t = undefined;
        }
        if (n === false) {
            n = qe;
        }
        return this.each(function() {
            ce.event.remove(this, e, n, t);
        });
    }
});
const Oe = /<script|<style|<link/i;
const Pe = /checked\s*(?:[^=]|=\s*.checked.)/i;
const Me = /^\s*<!\[CDATA\[|\]\]>\s*$/g;
function Re(e, t) {
    return fe(e, "table") && fe(t.nodeType !== 11 ? t : t.firstChild, "tr") && ce(e).children("tbody")[0] || e;
}
function Ie(e) {
    e.type = `${e.getAttribute("type") !== null}/${e.type}`;
    return e;
}
function We(e) {
    if ((e.type || "").slice(0, 5) === "true/") {
        e.type = e.type.slice(5);
    } else {
        e.removeAttribute("type");
    }
    return e;
}
function Fe(e, t) {
    let n;
    let r;
    let i;
    let o;
    let a;
    let s;
    if (t.nodeType === 1) {
        if (_.hasData(e) && (s = _.get(e).events)) {
            _.remove(t, "handle events");
            for(i in s){
                n = 0;
                for(r = s[i].length; n < r; n++){
                    ce.event.add(t, i, s[i][n]);
                }
            }
        }
        if (z.hasData(e)) {
            o = z.access(e);
            a = ce.extend({}, o);
            z.set(t, a);
        }
    }
}
function $e(n, r, i, o) {
    r = g(r);
    let e;
    let t;
    let a;
    let s;
    let u;
    let l;
    let c = 0;
    const n_length = n.length;
    const p = n_length - 1;
    const d = r[0];
    const h = v(d);
    if (h || n_length > 1 && typeof d === "string" && !support.checkClone && Pe.test(d)) {
        return n.each(function(e) {
            const t = n.eq(e);
            if (h) {
                r[0] = d.call(this, e, t.html());
            }
            $e(t, r, i, o);
        });
    }
    if (n_length && (t = (e = Ae(r, n[0].ownerDocument, false, n, o)).firstChild, e.childNodes.length === 1 && (e = t), t || o)) {
        for(s = (a = ce.map(Se(e, "script"), Ie)).length; c < n_length; c++){
            u = e;
            if (c !== p) {
                u = ce.clone(u, true, true);
                if (s) {
                    ce.merge(a, Se(u, "script"));
                }
            }
            i.call(n[c], u, c);
        }
        if (s) {
            l = a[a.length - 1].ownerDocument;
            ce.map(a, We);
            for(c = 0; c < s; c++){
                u = a[c];
                if (Ce.test(u.type || "") && !_.access(u, "globalEval") && ce.contains(l, u)) {
                    if (u.src && (u.type || "").toLowerCase() !== "module") {
                        if (ce._evalUrl && !u.noModule) {
                            ce._evalUrl(u.src, {
                                nonce: u.nonce || u.getAttribute("nonce")
                            }, l);
                        }
                    } else {
                        m(u.textContent.replace(Me, ""), u, l);
                    }
                }
            }
        }
    }
    return n;
}
function Be(e, t, n) {
    let r;
    for(let i = t ? ce.filter(t, e) : e, o = 0; (r = i[o]) != null; o++){
        if (!(n || r.nodeType !== 1)) {
            ce.cleanData(Se(r));
        }
        if (r.parentNode) {
            if (n && K(r)) {
                Ee(Se(r, "script"));
            }
            r.parentNode.removeChild(r);
        }
    }
    return e;
}
ce.extend({
    htmlPrefilter: function(e) {
        return e;
    },
    clone: function(e, t, n) {
        let r;
        let i;
        let o;
        let a;
        let s;
        let u;
        let l;
        const c = e.cloneNode(true);
        const f = K(e);
        if (!(support.noCloneChecked || e.nodeType !== 1 && e.nodeType !== 11 || ce.isXMLDoc(e))) {
            a = Se(c);
            r = 0;
            for(i = (o = Se(e)).length; r < i; r++){
                s = o[r];
                u = a[r];
                if ((l = u.nodeName.toLowerCase()) === "input" && we.test(s.type)) {
                    u.checked = s.checked;
                } else if (!(l !== "input" && l !== "textarea")) {
                    u.defaultValue = s.defaultValue;
                }
            }
        }
        if (t) {
            if (n) {
                o = o || Se(e);
                a = a || Se(c);
                r = 0;
                for(i = o.length; r < i; r++){
                    Fe(o[r], a[r]);
                }
            } else {
                Fe(e, c);
            }
        }
        if ((a = Se(c, "script")).length > 0) {
            Ee(a, !f && Se(e, "script"));
        }
        return c;
    },
    cleanData: function(e) {
        let t;
        let n;
        let r;
        const special = ce.event.special;
        for(let o = 0; (n = e[o]) !== undefined; o++){
            if ($(n)) {
                if (t = n[_.expando]) {
                    if (t.events) {
                        for(r in t.events){
                            if (special[r]) {
                                ce.event.remove(n, r);
                            } else {
                                ce.removeEvent(n, r, t.handle);
                            }
                        }
                    }
                    n[_.expando] = undefined;
                }
                if (n[z.expando]) {
                    n[z.expando] = undefined;
                }
            }
        }
    }
});
ce.fn.extend({
    detach: function(e) {
        return Be(this, e, true);
    },
    remove: function(e) {
        return Be(this, e);
    },
    text: function(e) {
        return M(this, function(e) {
            if (e === undefined) {
                return ce.text(this);
            }
            return this.empty().each(function() {
                if (!(this.nodeType !== 1 && this.nodeType !== 11 && this.nodeType !== 9)) {
                    this.textContent = e;
                }
            });
        }, null, e, arguments.length);
    },
    append: function() {
        return $e(this, arguments, function(e) {
            if (!(this.nodeType !== 1 && this.nodeType !== 11 && this.nodeType !== 9)) {
                Re(this, e).appendChild(e);
            }
        });
    },
    prepend: function() {
        return $e(this, arguments, function(e) {
            if (this.nodeType === 1 || this.nodeType === 11 || this.nodeType === 9) {
                const t = Re(this, e);
                t.insertBefore(e, t.firstChild);
            }
        });
    },
    before: function() {
        return $e(this, arguments, function(e) {
            if (this.parentNode) {
                this.parentNode.insertBefore(e, this);
            }
        });
    },
    after: function() {
        return $e(this, arguments, function(e) {
            if (this.parentNode) {
                this.parentNode.insertBefore(e, this.nextSibling);
            }
        });
    },
    empty: function() {
        let e;
        for(let t = 0; (e = this[t]) != null; t++){
            if (e.nodeType === 1) {
                ce.cleanData(Se(e, false));
                e.textContent = "";
            }
        }
        return this;
    },
    clone: function(e, t) {
        e = e != null && e;
        t = t ?? e;
        return this.map(function() {
            return ce.clone(this, e, t);
        });
    },
    html: function(e) {
        return M(this, function(e) {
            let t = this[0] || {};
            let n = 0;
            const length = this.length;
            if (e === undefined && t.nodeType === 1) {
                return t.innerHTML;
            }
            if (typeof e === "string" && !Oe.test(e) && !ke[(Te.exec(e) || [
                "",
                ""
            ])[1].toLowerCase()]) {
                e = ce.htmlPrefilter(e);
                try {
                    for(; n < length; n++){
                        if ((t = this[n] || {}).nodeType === 1) {
                            ce.cleanData(Se(t, false));
                            t.innerHTML = e;
                        }
                    }
                    t = 0;
                } catch (e) {}
            }
            if (t) {
                this.empty().append(e);
            }
        }, null, e, arguments.length);
    },
    replaceWith: function() {
        const n = [];
        return $e(this, arguments, function(e) {
            const parentNode = this.parentNode;
            if (ce.inArray(this, n) < 0) {
                ce.cleanData(Se(this));
                if (parentNode) {
                    parentNode.replaceChild(e, this);
                }
            }
        }, n);
    }
});
ce.each({
    appendTo: "append",
    prependTo: "prepend",
    insertBefore: "before",
    insertAfter: "after",
    replaceAll: "replaceWith"
}, function(e, a) {
    ce.fn[e] = function(e) {
        let t;
        const n = [];
        const r = ce(e);
        for(let i = r.length - 1, o = 0; o <= i; o++){
            t = o === i ? this : this.clone(true);
            ce(r[o])[a](t);
            push.apply(n, t.get());
        }
        return this.pushStack(n);
    };
});
const _e = new RegExp(`^(${source})(?!px)[a-z%]+\$`, "i");
const ze = /^--/;
const Xe = (e)=>{
    let defaultView = e.ownerDocument.defaultView;
    if (!(defaultView && defaultView.opener)) {
        defaultView = ie;
    }
    return defaultView.getComputedStyle(e);
};
const Ue = (e, t, n)=>{
    let r;
    let i;
    const o = {};
    for(i in t){
        o[i] = e.style[i];
        e.style[i] = t[i];
    }
    r = n.call(e);
    for(i in t){
        e.style[i] = o[i];
    }
    return r;
};
const Ve = new RegExp(Q.join("|"), "i");
function Ge(e, t, n) {
    let r;
    let i;
    let o;
    let a;
    const s = ze.test(t);
    const e_style = e.style;
    if (n = n || Xe(e)) {
        a = n.getPropertyValue(t) || n[t];
        if (s && a) {
            a = a.replace(ve, "$1") || undefined;
        }
        if (!(a !== "" || K(e))) {
            a = ce.style(e, t);
        }
        if (!support.pixelBoxStyles() && _e.test(a) && Ve.test(t)) {
            r = e_style.width;
            i = e_style.minWidth;
            o = e_style.maxWidth;
            e_style.minWidth = e_style.maxWidth = e_style.width = a;
            a = n.width;
            e_style.width = r;
            e_style.minWidth = i;
            e_style.maxWidth = o;
        }
    }
    if (a !== undefined) {
        return `${a}`;
    }
    return a;
}
function Ye(e, t) {
    return {
        get: function() {
            if (!e()) {
                return (this.get = t).apply(this, arguments);
            }
            delete this.get;
        }
    };
}
(()=>{
    function e() {
        if (l) {
            u.style.cssText = "position:absolute;left:-11111px;width:60px;margin-top:1px;padding:0;border:0";
            l.style.cssText = "position:relative;display:block;box-sizing:border-box;overflow:scroll;margin:auto;border:1px;padding:1px;width:60%;top:1%";
            C_documentElement.appendChild(u).appendChild(l);
            const e = ie.getComputedStyle(l);
            n = e.top !== "1%";
            s = t(e.marginLeft) === 12;
            l.style.right = "60%";
            o = t(e.right) === 36;
            r = t(e.width) === 36;
            l.style.position = "absolute";
            i = t(l.offsetWidth / 3) === 12;
            C_documentElement.removeChild(u);
            l = null;
        }
    }
    function t(e) {
        return Math.round(parseFloat(e));
    }
    var n;
    var r;
    var i;
    var o;
    let a;
    var s;
    var u = ie_document.createElement("div");
    var l = ie_document.createElement("div");
    if (l.style) {
        l.style.backgroundClip = "content-box";
        l.cloneNode(true).style.backgroundClip = "";
        support.clearCloneStyle = l.style.backgroundClip === "content-box";
        ce.extend(support, {
            boxSizingReliable: function() {
                e();
                return r;
            },
            pixelBoxStyles: function() {
                e();
                return o;
            },
            pixelPosition: function() {
                e();
                return n;
            },
            reliableMarginLeft: function() {
                e();
                return s;
            },
            scrollboxSize: function() {
                e();
                return i;
            },
            reliableTrDimensions: function() {
                let e;
                let t;
                let n;
                let r;
                if (a == null) {
                    e = ie_document.createElement("table");
                    t = ie_document.createElement("tr");
                    n = ie_document.createElement("div");
                    e.style.cssText = "position:absolute;left:-11111px;border-collapse:separate";
                    t.style.cssText = "box-sizing:content-box;border:1px solid";
                    t.style.height = "1px";
                    n.style.height = "9px";
                    n.style.display = "block";
                    C_documentElement.appendChild(e).appendChild(t).appendChild(n);
                    r = ie.getComputedStyle(t);
                    a = parseInt(r.height, 10) + parseInt(r.borderTopWidth, 10) + parseInt(r.borderBottomWidth, 10) === t.offsetHeight;
                    C_documentElement.removeChild(e);
                }
                return a;
            }
        });
    }
})();
const Qe = [
    "Webkit",
    "Moz",
    "ms"
];
const style = ie_document.createElement("div").style;
const Ke = {};
function Ze(e) {
    const t = ce.cssProps[e] || Ke[e];
    return t || (e in style ? e : Ke[e] = ((e)=>{
        const t = e[0].toUpperCase() + e.slice(1);
        let Qe_length = Qe.length;
        while(Qe_length--){
            if ((e = Qe[Qe_length] + t) in style) {
                return e;
            }
        }
    })(e) || e);
}
const et = /^(none|table(?!-c[ea]).+)/;
const tt = {
    position: "absolute",
    visibility: "hidden",
    display: "block"
};
const nt = {
    letterSpacing: "0",
    fontWeight: "400"
};
function rt(e, t, n) {
    const r = Y.exec(t);
    if (r) {
        return Math.max(0, r[2] - (n || 0)) + (r[3] || "px");
    }
    return t;
}
function it(e, t, n, r, i, o) {
    let a = t === "width" ? 1 : 0;
    let s = 0;
    let u = 0;
    let l = 0;
    if (n === (r ? "border" : "content")) {
        return 0;
    }
    for(; a < 4; a += 2){
        if (n === "margin") {
            l += ce.css(e, n + Q[a], true, i);
        }
        if (r) {
            if (n === "content") {
                u -= ce.css(e, `padding${Q[a]}`, true, i);
            }
            if (n !== "margin") {
                u -= ce.css(e, `border${Q[a]}Width`, true, i);
            }
        } else {
            u += ce.css(e, `padding${Q[a]}`, true, i);
            if (n !== "padding") {
                u += ce.css(e, `border${Q[a]}Width`, true, i);
            } else {
                s += ce.css(e, `border${Q[a]}Width`, true, i);
            }
        }
    }
    if (!r && o >= 0) {
        u += Math.max(0, Math.ceil(e[`offset${t[0].toUpperCase()}${t.slice(1)}`] - o - u - s - 0.5)) || 0;
    }
    return u + l;
}
function ot(e, t, n) {
    const r = Xe(e);
    let i = (!support.boxSizingReliable() || n) && ce.css(e, "boxSizing", false, r) === "border-box";
    let o = i;
    let a = Ge(e, t, r);
    const s = `offset${t[0].toUpperCase()}${t.slice(1)}`;
    if (_e.test(a)) {
        if (!n) {
            return a;
        }
        a = "auto";
    }
    if ((!support.boxSizingReliable() && i || !support.reliableTrDimensions() && fe(e, "tr") || a === "auto" || !parseFloat(a) && ce.css(e, "display", false, r) === "inline") && e.getClientRects().length) {
        i = ce.css(e, "boxSizing", false, r) === "border-box";
        if (o = s in e) {
            a = e[s];
        }
    }
    return `${(a = parseFloat(a) || 0) + it(e, t, n || (i ? "border" : "content"), o, r, a)}px`;
}
function at(e, t, n, r, i) {
    return new at.prototype.init(e, t, n, r, i);
}
ce.extend({
    cssHooks: {
        opacity: {
            get: function(e, t) {
                if (t) {
                    const n = Ge(e, "opacity");
                    if (n === "") {
                        return "1";
                    }
                    return n;
                }
            }
        }
    },
    cssNumber: {
        animationIterationCount: true,
        aspectRatio: true,
        borderImageSlice: true,
        columnCount: true,
        flexGrow: true,
        flexShrink: true,
        fontWeight: true,
        gridArea: true,
        gridColumn: true,
        gridColumnEnd: true,
        gridColumnStart: true,
        gridRow: true,
        gridRowEnd: true,
        gridRowStart: true,
        lineHeight: true,
        opacity: true,
        order: true,
        orphans: true,
        scale: true,
        widows: true,
        zIndex: true,
        zoom: true,
        fillOpacity: true,
        floodOpacity: true,
        stopOpacity: true,
        strokeMiterlimit: true,
        strokeOpacity: true
    },
    cssProps: {},
    style: function(e, t, n, r) {
        if (e && e.nodeType !== 3 && e.nodeType !== 8 && e.style) {
            let i;
            let o;
            let a;
            const s = F(t);
            const u = ze.test(t);
            const l = e.style;
            if (!u) {
                t = Ze(s);
            }
            a = ce.cssHooks[t] || ce.cssHooks[s];
            if (n === undefined) {
                if (a && "get" in a && (i = a.get(e, false, r)) !== undefined) {
                    return i;
                }
                return l[t];
            }
            if ((o = typeof n) === "string" && (i = Y.exec(n)) && i[1]) {
                n = te(e, t, i);
                o = "number";
            }
            if (n != null && n == n) {
                if (!(o !== "number" || u)) {
                    n += i && i[3] || (ce.cssNumber[s] ? "" : "px");
                }
                if (!(support.clearCloneStyle || n !== "" || t.indexOf("background") !== 0)) {
                    l[t] = "inherit";
                }
                if (!(a && "set" in a && (n = a.set(e, n, r)) === undefined)) {
                    if (u) {
                        l.setProperty(t, n);
                    } else {
                        l[t] = n;
                    }
                }
            }
        }
    },
    css: function(e, t, n, r) {
        let i;
        let o;
        let a;
        const s = F(t);
        if (!ze.test(t)) {
            t = Ze(s);
        }
        if ((a = ce.cssHooks[t] || ce.cssHooks[s]) && "get" in a) {
            i = a.get(e, true, n);
        }
        if (i === undefined) {
            i = Ge(e, t, r);
        }
        if (i === "normal" && t in nt) {
            i = nt[t];
        }
        if (n === "" || n) {
            o = parseFloat(i);
            if (n === true || isFinite(o)) {
                return o || 0;
            }
            return i;
        }
        return i;
    }
});
ce.each([
    "height",
    "width"
], function(e, u) {
    ce.cssHooks[u] = {
        get: function(e, t, n) {
            if (t) {
                if (!et.test(ce.css(e, "display")) || e.getClientRects().length && e.getBoundingClientRect().width) {
                    return ot(e, u, n);
                }
                return Ue(e, tt, ()=>ot(e, u, n));
            }
        },
        set: function(e, t, n) {
            let r;
            const i = Xe(e);
            const o = !support.scrollboxSize() && i.position === "absolute";
            const a = (o || n) && ce.css(e, "boxSizing", false, i) === "border-box";
            let s = n ? it(e, u, n, a, i) : 0;
            if (a && o) {
                s -= Math.ceil(e[`offset${u[0].toUpperCase()}${u.slice(1)}`] - parseFloat(i[u]) - it(e, u, "border", false, i) - 0.5);
            }
            if (s && (r = Y.exec(t)) && (r[3] || "px") !== "px") {
                e.style[u] = t;
                t = ce.css(e, u);
            }
            return rt(0, t, s);
        }
    };
});
ce.cssHooks.marginLeft = Ye(support.reliableMarginLeft, function(e, t) {
    if (t) {
        return `${parseFloat(Ge(e, "marginLeft")) || e.getBoundingClientRect().left - Ue(e, {
            marginLeft: 0
        }, ()=>e.getBoundingClientRect().left)}px`;
    }
});
ce.each({
    margin: "",
    padding: "",
    border: "Width"
}, function(i, o) {
    ce.cssHooks[i + o] = {
        expand: function(e) {
            for(var t = 0, n = {}, r = typeof e === "string" ? e.split(" ") : [
                e
            ]; t < 4; t++){
                n[i + Q[t] + o] = r[t] || r[t - 2] || r[0];
            }
            return n;
        }
    };
    if (i !== "margin") {
        ce.cssHooks[i + o].set = rt;
    }
});
ce.fn.extend({
    css: function(e, t) {
        return M(this, function(e, t, n) {
            let r;
            let i;
            const o = {};
            let a = 0;
            if (Array.isArray(t)) {
                r = Xe(e);
                for(i = t.length; a < i; a++){
                    o[t[a]] = ce.css(e, t[a], false, r);
                }
                return o;
            }
            if (n !== undefined) {
                return ce.style(e, t, n);
            }
            return ce.css(e, t);
        }, e, t, arguments.length > 1);
    }
});
((ce.Tween = at).prototype = {
    constructor: at,
    init: function(e, t, n, r, i, o) {
        this.elem = e;
        this.prop = n;
        this.easing = i || ce.easing._default;
        this.options = t;
        this.start = this.now = this.cur();
        this.end = r;
        this.unit = o || (ce.cssNumber[n] ? "" : "px");
    },
    cur: function() {
        const e = at.propHooks[this.prop];
        if (e && e.get) {
            return e.get(this);
        }
        return at.propHooks._default.get(this);
    },
    run: function(e) {
        let t;
        const n = at.propHooks[this.prop];
        if (this.options.duration) {
            this.pos = t = ce.easing[this.easing](e, this.options.duration * e, 0, 1, this.options.duration);
        } else {
            this.pos = t = e;
        }
        this.now = (this.end - this.start) * t + this.start;
        if (this.options.step) {
            this.options.step.call(this.elem, this.now, this);
        }
        if (n && n.set) {
            n.set(this);
        } else {
            at.propHooks._default.set(this);
        }
        return this;
    }
}).init.prototype = at.prototype;
(at.propHooks = {
    _default: {
        get: function(e) {
            let t;
            if (e.elem.nodeType !== 1 || e.elem[e.prop] != null && e.elem.style[e.prop] == null) {
                return e.elem[e.prop];
            }
            if ((t = ce.css(e.elem, e.prop, "")) && t !== "auto") {
                return t;
            }
            return 0;
        },
        set: function(e) {
            if (ce.fx.step[e.prop]) {
                ce.fx.step[e.prop](e);
            } else if (e.elem.nodeType !== 1 || !ce.cssHooks[e.prop] && e.elem.style[Ze(e.prop)] == null) {
                e.elem[e.prop] = e.now;
            } else {
                ce.style(e.elem, e.prop, e.now + e.unit);
            }
        }
    }
}).scrollTop = at.propHooks.scrollLeft = {
    set: function(e) {
        if (e.elem.nodeType && e.elem.parentNode) {
            e.elem[e.prop] = e.now;
        }
    }
};
ce.easing = {
    linear: function(e) {
        return e;
    },
    swing: function(e) {
        return 0.5 - Math.cos(e * Math.PI) / 2;
    },
    _default: "swing"
};
ce.fx = at.prototype.init;
ce.fx.step = {};
let st;
let ut;
let lt;
let ct;
const ft = /^(?:toggle|show|hide)$/;
const pt = /queueHooks$/;
function dt() {
    if (ut) {
        if (ie_document.hidden === false && ie.requestAnimationFrame) {
            ie.requestAnimationFrame(dt);
        } else {
            ie.setTimeout(dt, ce.fx.interval);
        }
        ce.fx.tick();
    }
}
function ht() {
    ie.setTimeout(function() {
        st = undefined;
    });
    return st = Date.now();
}
function gt(height, t) {
    let n;
    let r = 0;
    const i = {
        height
    };
    for(t = t ? 1 : 0; r < 4; r += 2 - t){
        i[`margin${n = Q[r]}`] = i[`padding${n}`] = height;
    }
    if (t) {
        i.opacity = i.width = height;
    }
    return i;
}
function vt(e, t, n) {
    let r;
    const i = (yt.tweeners[t] || []).concat(yt.tweeners["*"]);
    for(let o = 0, a = i.length; o < a; o++){
        if (r = i[o].call(n, t, e)) {
            return r;
        }
    }
}
function yt(elem, originalProperties, originalOptions) {
    let n;
    let a;
    let r = 0;
    const length = yt.prefilters.length;
    const s = ce.Deferred().always(function() {
        delete u.elem;
    });
    var u = function() {
        if (a) {
            return false;
        }
        const e = st || ht();
        const t = Math.max(0, anim.startTime + anim.duration - e);
        const n = 1 - (t / anim.duration || 0);
        for(var r = 0, i = anim.tweens.length; r < i; r++){
            anim.tweens[r].run(n);
        }
        s.notifyWith(elem, [
            anim,
            n,
            t
        ]);
        if (n < 1 && i) {
            return t;
        }
        if (!i) {
            s.notifyWith(elem, [
                anim,
                1,
                0
            ]);
        }
        s.resolveWith(elem, [
            anim
        ]);
        return false;
    };
    var anim = s.promise({
        elem,
        props: ce.extend({}, originalProperties),
        opts: ce.extend(true, {
            specialEasing: {},
            easing: ce.easing._default
        }, originalOptions),
        originalProperties,
        originalOptions,
        startTime: st || ht(),
        duration: originalOptions.duration,
        tweens: [],
        createTween: function(e, t) {
            const n = ce.Tween(elem, anim.opts, e, t, anim.opts.specialEasing[e] || anim.opts.easing);
            anim.tweens.push(n);
            return n;
        },
        stop: function(e) {
            let t = 0;
            const n = e ? anim.tweens.length : 0;
            if (a) {
                return this;
            }
            for(a = true; t < n; t++){
                anim.tweens[t].run(1);
            }
            if (e) {
                s.notifyWith(elem, [
                    anim,
                    1,
                    0
                ]);
                s.resolveWith(elem, [
                    anim,
                    e
                ]);
            } else {
                s.rejectWith(elem, [
                    anim,
                    e
                ]);
            }
            return this;
        }
    });
    const l_props = anim.props;
    for(!((l_props_1, t)=>{
        let n;
        let r;
        let i;
        let o;
        let a;
        for(n in l_props_1){
            i = t[r = F(n)];
            o = l_props_1[n];
            if (Array.isArray(o)) {
                i = o[1];
                o = l_props_1[n] = o[0];
            }
            if (n !== r) {
                l_props_1[r] = o;
                delete l_props_1[n];
            }
            if ((a = ce.cssHooks[r]) && "expand" in a) {
                o = a.expand(o);
                delete l_props_1[r];
                for(n in o){
                    if (!(n in l_props_1)) {
                        l_props_1[n] = o[n];
                        t[n] = i;
                    }
                }
            } else {
                t[r] = i;
            }
        }
    })(l_props, anim.opts.specialEasing); r < length; r++){
        if (n = yt.prefilters[r].call(anim, elem, l_props, anim.opts)) {
            if (v(n.stop)) {
                ce._queueHooks(anim.elem, anim.opts.queue).stop = n.stop.bind(n);
            }
            return n;
        }
    }
    ce.map(l_props, vt, anim);
    if (v(anim.opts.start)) {
        anim.opts.start.call(elem, anim);
    }
    anim.progress(anim.opts.progress).done(anim.opts.done, anim.opts.complete).fail(anim.opts.fail).always(anim.opts.always);
    ce.fx.timer(ce.extend(u, {
        elem,
        anim,
        queue: anim.opts.queue
    }));
    return anim;
}
ce.Animation = ce.extend(yt, {
    tweeners: {
        "*": [
            function(e, t) {
                const n = this.createTween(e, t);
                te(n.elem, e, Y.exec(t), n);
                return n;
            }
        ]
    },
    tweener: function(e, t) {
        if (v(e)) {
            t = e;
            e = [
                "*"
            ];
        } else {
            e = e.match(D);
        }
        let n;
        for(let r = 0, i = e.length; r < i; r++){
            n = e[r];
            yt.tweeners[n] = yt.tweeners[n] || [];
            yt.tweeners[n].unshift(t);
        }
    },
    prefilters: [
        function(e, t, n) {
            let r;
            let i;
            let o;
            let a;
            let s;
            let u;
            let display;
            let c;
            const f = "width" in t || "height" in t;
            const p = this;
            const d = {};
            const e_style = e.style;
            let g = e.nodeType && ee(e);
            let v = _.get(e, "fxshow");
            if (!n.queue) {
                if ((a = ce._queueHooks(e, "fx")).unqueued == null) {
                    a.unqueued = 0;
                    s = a.empty.fire;
                    a.empty.fire = function() {
                        if (!a.unqueued) {
                            s();
                        }
                    };
                }
                a.unqueued++;
                p.always(function() {
                    p.always(function() {
                        a.unqueued--;
                        if (!ce.queue(e, "fx").length) {
                            a.empty.fire();
                        }
                    });
                });
            }
            for(r in t){
                i = t[r];
                if (ft.test(i)) {
                    delete t[r];
                    o = o || i === "toggle";
                    if (i === (g ? "hide" : "show")) {
                        if (i !== "show" || !v || v[r] === undefined) {
                            continue;
                        }
                        g = true;
                    }
                    d[r] = v && v[r] || ce.style(e, r);
                }
            }
            if ((u = !ce.isEmptyObject(t)) || !ce.isEmptyObject(d)) {
                if (f && e.nodeType === 1) {
                    n.overflow = [
                        e_style.overflow,
                        e_style.overflowX,
                        e_style.overflowY
                    ];
                    if ((display = v && v.display) == null) {
                        display = _.get(e, "display");
                    }
                    if ((c = ce.css(e, "display")) === "none") {
                        if (display) {
                            c = display;
                        } else {
                            re([
                                e
                            ], true);
                            display = e.style.display || display;
                            c = ce.css(e, "display");
                            re([
                                e
                            ]);
                        }
                    }
                    if ((c === "inline" || c === "inline-block" && display != null) && ce.css(e, "float") === "none") {
                        if (!u) {
                            p.done(function() {
                                e_style.display = display;
                            });
                            if (display == null) {
                                c = e_style.display;
                                display = c === "none" ? "" : c;
                            }
                        }
                        e_style.display = "inline-block";
                    }
                }
                if (n.overflow) {
                    e_style.overflow = "hidden";
                    p.always(function() {
                        e_style.overflow = n.overflow[0];
                        e_style.overflowX = n.overflow[1];
                        e_style.overflowY = n.overflow[2];
                    });
                }
                u = false;
                for(r in d){
                    if (!u) {
                        if (v) {
                            if ("hidden" in v) {
                                g = v.hidden;
                            }
                        } else {
                            v = _.access(e, "fxshow", {
                                display
                            });
                        }
                        if (o) {
                            v.hidden = !g;
                        }
                        if (g) {
                            re([
                                e
                            ], true);
                        }
                        p.done(function() {
                            if (!g) {
                                re([
                                    e
                                ]);
                            }
                            _.remove(e, "fxshow");
                            for(r in d){
                                ce.style(e, r, d[r]);
                            }
                        });
                    }
                    u = vt(g ? v[r] : 0, r, p);
                    if (!(r in v)) {
                        v[r] = u.start;
                        if (g) {
                            u.end = u.start;
                            u.start = 0;
                        }
                    }
                }
            }
        }
    ],
    prefilter: function(e, t) {
        if (t) {
            yt.prefilters.unshift(e);
        } else {
            yt.prefilters.push(e);
        }
    }
});
ce.speed = function(duration, t, n) {
    const r = duration && typeof duration === "object" ? ce.extend({}, duration) : {
        complete: n || !n && t || v(duration) && duration,
        duration,
        easing: n && t || t && !v(t) && t
    };
    if (ce.fx.off) {
        r.duration = 0;
    } else {
        if (typeof r.duration !== "number") {
            if (r.duration in ce.fx.speeds) {
                r.duration = ce.fx.speeds[r.duration];
            } else {
                r.duration = ce.fx.speeds._default;
            }
        }
    }
    if (!(r.queue != null && r.queue !== true)) {
        r.queue = "fx";
    }
    r.old = r.complete;
    r.complete = function() {
        if (v(r.old)) {
            r.old.call(this);
        }
        if (r.queue) {
            ce.dequeue(this, r.queue);
        }
    };
    return r;
};
ce.fn.extend({
    fadeTo: function(e, opacity, n, r) {
        return this.filter(ee).css("opacity", 0).show().end().animate({
            opacity
        }, e, n, r);
    },
    animate: function(t, e, n, r) {
        const i = ce.isEmptyObject(t);
        const o = ce.speed(e, n, r);
        const a = function() {
            const e = yt(this, ce.extend({}, t), o);
            if (i || _.get(this, "finish")) {
                e.stop(true);
            }
        };
        a.finish = a;
        if (i || o.queue === false) {
            return this.each(a);
        }
        return this.queue(o.queue, a);
    },
    stop: function(i, e, o) {
        const a = (e)=>{
            const e_stop = e.stop;
            delete e.stop;
            e_stop(o);
        };
        if (typeof i !== "string") {
            o = e;
            e = i;
            i = undefined;
        }
        if (e) {
            this.queue(i || "fx", []);
        }
        return this.each(function() {
            let e = true;
            let t = i != null && `${i}queueHooks`;
            const ce_timers = ce.timers;
            const r = _.get(this);
            if (t) {
                if (r[t] && r[t].stop) {
                    a(r[t]);
                }
            } else {
                for(t in r){
                    if (r[t] && r[t].stop && pt.test(t)) {
                        a(r[t]);
                    }
                }
            }
            for(t = ce_timers.length; t--;){
                if (!(ce_timers[t].elem !== this || i != null && ce_timers[t].queue !== i)) {
                    ce_timers[t].anim.stop(o);
                    e = false;
                    ce_timers.splice(t, 1);
                }
            }
            if (!(!e && o)) {
                ce.dequeue(this, i);
            }
        });
    },
    finish: function(a) {
        if (a !== false) {
            a = a || "fx";
        }
        return this.each(function() {
            let e;
            const t = _.get(this);
            const n = t[`${a}queue`];
            const r = t[`${a}queueHooks`];
            const ce_timers = ce.timers;
            const o = n ? n.length : 0;
            t.finish = true;
            ce.queue(this, a, []);
            if (r && r.stop) {
                r.stop.call(this, true);
            }
            for(e = ce_timers.length; e--;){
                if (ce_timers[e].elem === this && ce_timers[e].queue === a) {
                    ce_timers[e].anim.stop(true);
                    ce_timers.splice(e, 1);
                }
            }
            for(e = 0; e < o; e++){
                if (n[e] && n[e].finish) {
                    n[e].finish.call(this);
                }
            }
            delete t.finish;
        });
    }
});
ce.each([
    "toggle",
    "show",
    "hide"
], function(e, r) {
    const i = ce.fn[r];
    ce.fn[r] = function(e, t, n) {
        if (e == null || typeof e === "boolean") {
            return i.apply(this, arguments);
        }
        return this.animate(gt(r, true), e, t, n);
    };
});
ce.each({
    slideDown: gt("show"),
    slideUp: gt("hide"),
    slideToggle: gt("toggle"),
    fadeIn: {
        opacity: "show"
    },
    fadeOut: {
        opacity: "hide"
    },
    fadeToggle: {
        opacity: "toggle"
    }
}, function(e, r) {
    ce.fn[e] = function(e, t, n) {
        return this.animate(r, e, t, n);
    };
});
ce.timers = [];
ce.fx.tick = function() {
    let e;
    let t = 0;
    const ce_timers = ce.timers;
    for(st = Date.now(); t < ce_timers.length; t++){
        if (!((e = ce_timers[t])() || ce_timers[t] !== e)) {
            ce_timers.splice(t--, 1);
        }
    }
    if (!ce_timers.length) {
        ce.fx.stop();
    }
    st = undefined;
};
ce.fx.timer = function(e) {
    ce.timers.push(e);
    ce.fx.start();
};
ce.fx.interval = 13;
ce.fx.start = function() {
    if (!ut) {
        ut = true;
        dt();
    }
};
ce.fx.stop = function() {
    ut = null;
};
ce.fx.speeds = {
    slow: 600,
    fast: 200,
    _default: 400
};
ce.fn.delay = function(r, e) {
    r = ce.fx && ce.fx.speeds[r] || r;
    e = e || "fx";
    return this.queue(e, function(e, t) {
        const n = ie.setTimeout(e, r);
        t.stop = function() {
            ie.clearTimeout(n);
        };
    });
};
lt = ie_document.createElement("input");
ct = ie_document.createElement("select").appendChild(ie_document.createElement("option"));
lt.type = "checkbox";
support.checkOn = lt.value !== "";
support.optSelected = ct.selected;
lt = ie_document.createElement("input");
lt.value = "t";
lt.type = "radio";
support.radioValue = lt.value === "t";
let mt;
const attrHandle = ce.expr.attrHandle;
ce.fn.extend({
    attr: function(e, t) {
        return M(this, ce.attr, e, t, arguments.length > 1);
    },
    removeAttr: function(e) {
        return this.each(function() {
            ce.removeAttr(this, e);
        });
    }
});
ce.extend({
    attr: function(e, t, n) {
        let r;
        let i;
        const e_nodeType = e.nodeType;
        if (e_nodeType !== 3 && e_nodeType !== 8 && e_nodeType !== 2) {
            if (typeof e.getAttribute === "undefined") {
                return ce.prop(e, t, n);
            }
            if (!(e_nodeType === 1 && ce.isXMLDoc(e))) {
                i = ce.attrHooks[t.toLowerCase()] || (ce.expr.match.bool.test(t) ? mt : undefined);
            }
            if (n !== undefined) {
                if (n === null) {
                    return void ce.removeAttr(e, t);
                }
                if (i && "set" in i && (r = i.set(e, n, t)) !== undefined) {
                    return r;
                }
                return e.setAttribute(t, `${n}`), n;
            }
            if (i && "get" in i && (r = i.get(e, t)) !== null) {
                return r;
            }
            if ((r = ce.find.attr(e, t)) == null) {
                return undefined;
            }
            return r;
        }
    },
    attrHooks: {
        type: {
            set: function(e, t) {
                if (!support.radioValue && t === "radio" && fe(e, "input")) {
                    const n = e.value;
                    e.setAttribute("type", t);
                    if (n) {
                        e.value = n;
                    }
                    return t;
                }
            }
        }
    },
    removeAttr: function(e, t) {
        let n;
        let r = 0;
        const i = t && t.match(D);
        if (i && e.nodeType === 1) {
            while(n = i[r++]){
                e.removeAttribute(n);
            }
        }
    }
});
mt = {
    set: function(e, t, n) {
        if (t === false) {
            ce.removeAttr(e, n);
        } else {
            e.setAttribute(n, n);
        }
        return n;
    }
};
ce.each(ce.expr.match.bool.source.match(/\w+/g), function(e, t) {
    const a = attrHandle[t] || ce.find.attr;
    attrHandle[t] = function(e, t, n) {
        let r;
        let i;
        const o = t.toLowerCase();
        if (!n) {
            i = attrHandle[o];
            attrHandle[o] = r;
            r = a(e, t, n) != null ? o : null;
            attrHandle[o] = i;
        }
        return r;
    };
});
const bt = /^(?:input|select|textarea|button)$/i;
const wt = /^(?:a|area)$/i;
function Tt(e) {
    return (e.match(D) || []).join(" ");
}
function Ct(e) {
    return e.getAttribute && e.getAttribute("class") || "";
}
function kt(e) {
    if (Array.isArray(e)) {
        return e;
    }
    return typeof e === "string" && e.match(D) || [];
}
ce.fn.extend({
    prop: function(e, t) {
        return M(this, ce.prop, e, t, arguments.length > 1);
    },
    removeProp: function(e) {
        return this.each(function() {
            delete this[ce.propFix[e] || e];
        });
    }
});
ce.extend({
    prop: function(e, t, n) {
        let r;
        let i;
        const e_nodeType = e.nodeType;
        if (e_nodeType !== 3 && e_nodeType !== 8 && e_nodeType !== 2) {
            if (!(e_nodeType === 1 && ce.isXMLDoc(e))) {
                t = ce.propFix[t] || t;
                i = ce.propHooks[t];
            }
            if (n !== undefined) {
                if (i && "set" in i && (r = i.set(e, n, t)) !== undefined) {
                    return r;
                }
                return e[t] = n;
            }
            if (i && "get" in i && (r = i.get(e, t)) !== null) {
                return r;
            }
            return e[t];
        }
    },
    propHooks: {
        tabIndex: {
            get: function(e) {
                const t = ce.find.attr(e, "tabindex");
                if (t) {
                    return parseInt(t, 10);
                }
                if (bt.test(e.nodeName) || wt.test(e.nodeName) && e.href) {
                    return 0;
                }
                return -1;
            }
        }
    },
    propFix: {
        for: "htmlFor",
        class: "className"
    }
});
if (!support.optSelected) {
    ce.propHooks.selected = {
        get: function({ parentNode }) {
            parentNode && parentNode.parentNode && parentNode.parentNode.selectedIndex;
            return null;
        },
        set: function({ parentNode }) {
            parentNode && (parentNode.selectedIndex, parentNode.parentNode && parentNode.parentNode.selectedIndex);
        }
    };
}
ce.each([
    "tabIndex",
    "readOnly",
    "maxLength",
    "cellSpacing",
    "cellPadding",
    "rowSpan",
    "colSpan",
    "useMap",
    "frameBorder",
    "contentEditable"
], function() {
    ce.propFix[this.toLowerCase()] = this;
});
ce.fn.extend({
    addClass: function(t) {
        let e;
        let n;
        let r;
        let i;
        let o;
        let a;
        if (v(t)) {
            return this.each(function(e) {
                ce(this).addClass(t.call(this, e, Ct(this)));
            });
        }
        if ((e = kt(t)).length) {
            return this.each(function() {
                r = Ct(this);
                if (n = this.nodeType === 1 && ` ${Tt(r)} `) {
                    for(o = 0; o < e.length; o++){
                        i = e[o];
                        if (n.indexOf(` ${i} `) < 0) {
                            n += `${i} `;
                        }
                    }
                    a = Tt(n);
                    if (r !== a) {
                        this.setAttribute("class", a);
                    }
                }
            });
        }
        return this;
    },
    removeClass: function(t) {
        let e;
        let n;
        let r;
        let i;
        let o;
        let a;
        if (v(t)) {
            return this.each(function(e) {
                ce(this).removeClass(t.call(this, e, Ct(this)));
            });
        }
        if (arguments.length) {
            if ((e = kt(t)).length) {
                return this.each(function() {
                    r = Ct(this);
                    if (n = this.nodeType === 1 && ` ${Tt(r)} `) {
                        for(o = 0; o < e.length; o++){
                            i = e[o];
                            while(n.indexOf(` ${i} `) > -1){
                                n = n.replace(` ${i} `, " ");
                            }
                        }
                        a = Tt(n);
                        if (r !== a) {
                            this.setAttribute("class", a);
                        }
                    }
                });
            }
            return this;
        }
        return this.attr("class", "");
    },
    toggleClass: function(t, n) {
        let e;
        let r;
        let i;
        let o;
        const a = typeof t;
        const s = a === "string" || Array.isArray(t);
        if (v(t)) {
            return this.each(function(e) {
                ce(this).toggleClass(t.call(this, e, Ct(this), n), n);
            });
        }
        if (typeof n === "boolean" && s) {
            if (n) {
                return this.addClass(t);
            }
            return this.removeClass(t);
        }
        e = kt(t);
        return this.each(function() {
            if (s) {
                o = ce(this);
                for(i = 0; i < e.length; i++){
                    r = e[i];
                    if (o.hasClass(r)) {
                        o.removeClass(r);
                    } else {
                        o.addClass(r);
                    }
                }
            } else {
                if (!(t !== undefined && a !== "boolean")) {
                    if (r = Ct(this)) {
                        _.set(this, "__className__", r);
                    }
                    if (this.setAttribute) {
                        this.setAttribute("class", r || t === false ? "" : _.get(this, "__className__") || "");
                    }
                }
            }
        });
    },
    hasClass: function(e) {
        let t;
        let n;
        let r = 0;
        t = ` ${e} `;
        while(n = this[r++]){
            if (n.nodeType === 1 && ` ${Tt(Ct(n))} `.indexOf(t) > -1) {
                return true;
            }
        }
        return false;
    }
});
const St = /\r/g;
ce.fn.extend({
    val: function(n) {
        let r;
        let e;
        let i;
        const t = this[0];
        if (arguments.length) {
            i = v(n);
            return this.each(function(e) {
                let t;
                if (this.nodeType === 1) {
                    if ((t = i ? n.call(this, e, ce(this).val()) : n) == null) {
                        t = "";
                    } else if (typeof t === "number") {
                        t += "";
                    } else if (Array.isArray(t)) {
                        t = ce.map(t, function(e) {
                            if (e == null) {
                                return "";
                            }
                            return `${e}`;
                        });
                    }
                    if (!((r = ce.valHooks[this.type] || ce.valHooks[this.nodeName.toLowerCase()]) && "set" in r && r.set(this, t, "value") !== undefined)) {
                        this.value = t;
                    }
                }
            });
        }
        if (t) {
            if ((r = ce.valHooks[t.type] || ce.valHooks[t.nodeName.toLowerCase()]) && "get" in r && (e = r.get(t, "value")) !== undefined) {
                return e;
            }
            if (typeof (e = t.value) === "string") {
                return e.replace(St, "");
            }
            return e ?? "";
        }
    }
});
ce.extend({
    valHooks: {
        option: {
            get: function(e) {
                const t = ce.find.attr(e, "value");
                return t ?? Tt(ce.text(e));
            }
        },
        select: {
            get: function(e) {
                let t;
                let n;
                let r;
                const { options, selectedIndex } = e;
                const a = e.type === "select-one";
                const s = a ? null : [];
                const u = a ? selectedIndex + 1 : options.length;
                for(r = selectedIndex < 0 ? u : a ? selectedIndex : 0; r < u; r++){
                    if (((n = options[r]).selected || r === selectedIndex) && !n.disabled && (!n.parentNode.disabled || !fe(n.parentNode, "optgroup"))) {
                        t = ce(n).val();
                        if (a) {
                            return t;
                        }
                        s.push(t);
                    }
                }
                return s;
            },
            set: function(e, t) {
                let n;
                let r;
                const e_options = e.options;
                const o = ce.makeArray(t);
                let i_length = e_options.length;
                while(i_length--){
                    if ((r = e_options[i_length]).selected = ce.inArray(ce.valHooks.option.get(r), o) > -1) {
                        n = true;
                    }
                }
                if (!n) {
                    e.selectedIndex = -1;
                }
                return o;
            }
        }
    }
});
ce.each([
    "radio",
    "checkbox"
], function() {
    ce.valHooks[this] = {
        set: function(e, t) {
            if (Array.isArray(t)) {
                return e.checked = ce.inArray(ce(e).val(), t) > -1;
            }
        }
    };
    if (!support.checkOn) {
        ce.valHooks[this].get = function(e) {
            if (e.getAttribute("value") === null) {
                return "on";
            }
            return e.value;
        };
    }
});
const ie_location = ie.location;
const jt = {
    guid: Date.now()
};
const At = /\?/;
ce.parseXML = function(e) {
    let t;
    let n;
    if (!e || typeof e !== "string") {
        return null;
    }
    try {
        t = (new ie.DOMParser).parseFromString(e, "text/xml");
    } catch (e) {}
    n = t && t.getElementsByTagName("parsererror")[0];
    if (!(t && !n)) {
        ce.error(`Invalid XML: ${n ? ce.map(n.childNodes, function(e) {
            return e.textContent;
        }).join("\n") : e}`);
    }
    return t;
};
const Dt = /^(?:focusinfocus|focusoutblur)$/;
const Nt = function(e) {
    e.stopPropagation();
};
ce.extend(ce.event, {
    trigger: function(e, t, n, r) {
        let i;
        let o;
        let a;
        let s;
        let u;
        let l;
        let c;
        let f;
        const p = [
            n || ie_document
        ];
        let d = hasOwnProperty.call(e, "type") ? e.type : e;
        let h = hasOwnProperty.call(e, "namespace") ? e.namespace.split(".") : [];
        o = f = a = n = n || ie_document;
        if (n.nodeType !== 3 && n.nodeType !== 8 && !Dt.test(d + ce.event.triggered) && (d.indexOf(".") > -1 && (d = (h = d.split(".")).shift(), h.sort()), u = d.indexOf(":") < 0 && `on${d}`, (e = e[ce.expando] ? e : new ce.Event(d, typeof e === "object" && e)).isTrigger = r ? 2 : 3, e.namespace = h.join("."), e.rnamespace = e.namespace ? new RegExp(`(^|\\.)${h.join("\\.(?:.*\\.|)")}(\\.|\$)`) : null, e.result = undefined, e.target || (e.target = n), t = t == null ? [
            e
        ] : ce.makeArray(t, [
            e
        ]), c = ce.event.special[d] || {}, r || !c.trigger || c.trigger.apply(n, t) !== false)) {
            if (!r && !c.noBubble && !y(n)) {
                s = c.delegateType || d;
                if (!Dt.test(s + d)) {
                    o = o.parentNode;
                }
                for(; o; o = o.parentNode){
                    p.push(o);
                    a = o;
                }
                if (a === (n.ownerDocument || ie_document)) {
                    p.push(a.defaultView || a.parentWindow || ie);
                }
            }
            i = 0;
            while((o = p[i++]) && !e.isPropagationStopped()){
                f = o;
                e.type = i > 1 ? s : c.bindType || d;
                if (l = (_.get(o, "events") || Object.create(null))[e.type] && _.get(o, "handle")) {
                    l.apply(o, t);
                }
                if ((l = u && o[u]) && l.apply && $(o)) {
                    e.result = l.apply(o, t);
                    if (e.result === false) {
                        e.preventDefault();
                    }
                }
            }
            e.type = d;
            if (!(r || e.isDefaultPrevented() || c._default && c._default.apply(p.pop(), t) !== false || !$(n))) {
                if (u && v(n[d]) && !y(n)) {
                    if (a = n[u]) {
                        n[u] = null;
                    }
                    ce.event.triggered = d;
                    if (e.isPropagationStopped()) {
                        f.addEventListener(d, Nt);
                    }
                    n[d]();
                    if (e.isPropagationStopped()) {
                        f.removeEventListener(d, Nt);
                    }
                    ce.event.triggered = undefined;
                    if (a) {
                        n[u] = a;
                    }
                }
            }
            return e.result;
        }
    },
    simulate: function(type, t, n) {
        const r = ce.extend(new ce.Event, n, {
            type,
            isSimulated: true
        });
        ce.event.trigger(r, null, t);
    }
});
ce.fn.extend({
    trigger: function(e, t) {
        return this.each(function() {
            ce.event.trigger(e, t, this);
        });
    },
    triggerHandler: function(e, t) {
        const n = this[0];
        if (n) {
            return ce.event.trigger(e, t, n, true);
        }
    }
});
const qt = /\[\]$/;
const Lt = /\r?\n/g;
const Ht = /^(?:submit|button|image|reset|file)$/i;
const Ot = /^(?:input|select|textarea|keygen)/i;
function Pt(n, e, r, i) {
    let t;
    if (Array.isArray(e)) {
        ce.each(e, function(e, t) {
            if (r || qt.test(n)) {
                i(n, t);
            } else {
                Pt(`${n}[${typeof t === "object" && t != null ? e : ""}]`, t, r, i);
            }
        });
    } else if (r || x(e) !== "object") {
        i(n, e);
    } else {
        for(t in e){
            Pt(`${n}[${t}]`, e[t], r, i);
        }
    }
}
ce.param = function(e, t) {
    let n;
    const r = [];
    const i = function(e, t) {
        const n = v(t) ? t() : t;
        r[r.length] = `${encodeURIComponent(e)}=${encodeURIComponent(n ?? "")}`;
    };
    if (e == null) {
        return "";
    }
    if (Array.isArray(e) || e.jquery && !ce.isPlainObject(e)) {
        ce.each(e, function() {
            i(this.name, this.value);
        });
    } else {
        for(n in e){
            Pt(n, e[n], t, i);
        }
    }
    return r.join("&");
};
ce.fn.extend({
    serialize: function() {
        return ce.param(this.serializeArray());
    },
    serializeArray: function() {
        return this.map(function() {
            const e = ce.prop(this, "elements");
            if (e) {
                return ce.makeArray(e);
            }
            return this;
        }).filter(function() {
            const type = this.type;
            return this.name && !ce(this).is(":disabled") && Ot.test(this.nodeName) && !Ht.test(type) && (this.checked || !we.test(type));
        }).map(function(e, t) {
            const n = ce(this).val();
            if (n == null) {
                return null;
            }
            if (Array.isArray(n)) {
                return ce.map(n, function(e) {
                    return {
                        name: t.name,
                        value: e.replace(Lt, "\r\n")
                    };
                });
            }
            return {
                name: t.name,
                value: n.replace(Lt, "\r\n")
            };
        }).get();
    }
});
const Mt = /%20/g;
const Rt = /#.*$/;
const It = /([?&])_=[^&]*/;
const Wt = /^(.*?):[ \t]*([^\r\n]*)$/gm;
const Ft = /^(?:GET|HEAD)$/;
const $t = /^\/\//;
const Bt = {};
const _t = {};
const zt = `*/*`;
const Xt = ie_document.createElement("a");
function Ut(o) {
    return function(e, t) {
        if (typeof e !== "string") {
            t = e;
            e = "*";
        }
        let n;
        let r = 0;
        const i = e.toLowerCase().match(D) || [];
        if (v(t)) {
            while(n = i[r++]){
                if (n[0] === "+") {
                    n = n.slice(1) || "*";
                    (o[n] = o[n] || []).unshift(t);
                } else {
                    (o[n] = o[n] || []).push(t);
                }
            }
        }
    };
}
function Vt(t, i, o, a) {
    const s = {};
    const u = t === _t;
    function l(e) {
        let r;
        s[e] = true;
        ce.each(t[e] || [], function(e, t) {
            const n = t(i, o, a);
            if (typeof n !== "string" || u || s[n]) {
                if (u) {
                    return !(r = n);
                }
                return undefined;
            }
            i.dataTypes.unshift(n);
            l(n);
            return false;
        });
        return r;
    }
    return l(i.dataTypes[0]) || !s["*"] && l("*");
}
function Gt(e, t) {
    let n;
    let r;
    const i = ce.ajaxSettings.flatOptions || {};
    for(n in t){
        if (t[n] !== undefined) {
            (i[n] ? e : r || (r = {}))[n] = t[n];
        }
    }
    if (r) {
        ce.extend(true, e, r);
    }
    return e;
}
Xt.href = ie_location.href;
ce.extend({
    active: 0,
    lastModified: {},
    etag: {},
    ajaxSettings: {
        url: ie_location.href,
        type: "GET",
        isLocal: /^(?:about|app|app-storage|.+-extension|file|res|widget):$/.test(ie_location.protocol),
        global: true,
        processData: true,
        async: true,
        contentType: "application/x-www-form-urlencoded; charset=UTF-8",
        accepts: {
            "*": zt,
            text: "text/plain",
            html: "text/html",
            xml: "application/xml, text/xml",
            json: "application/json, text/javascript"
        },
        contents: {
            xml: /\bxml\b/,
            html: /\bhtml/,
            json: /\bjson\b/
        },
        responseFields: {
            xml: "responseXML",
            text: "responseText",
            json: "responseJSON"
        },
        converters: {
            "* text": String,
            "text html": true,
            "text json": JSON.parse,
            "text xml": ce.parseXML
        },
        flatOptions: {
            url: true,
            context: true
        }
    },
    ajaxSetup: function(e, t) {
        if (t) {
            return Gt(Gt(e, ce.ajaxSettings), t);
        }
        return Gt(ce.ajaxSettings, e);
    },
    ajaxPrefilter: Ut(Bt),
    ajaxTransport: Ut(_t),
    ajax: function(e, t) {
        if (typeof e === "object") {
            t = e;
            e = undefined;
        }
        t = t || {};
        let c;
        let f;
        let p;
        let n;
        let d;
        let r;
        let h;
        let g;
        let i;
        let o;
        const v = ce.ajaxSetup({}, t);
        const y = v.context || v;
        const m = v.context && (y.nodeType || y.jquery) ? ce(y) : ce.event;
        const x = ce.Deferred();
        const b = ce.Callbacks("once memory");
        let w = v.statusCode || {};
        const a = {};
        const s = {};
        let u = "canceled";
        var T = {
            readyState: 0,
            getResponseHeader: function(e) {
                let t;
                if (h) {
                    if (!n) {
                        n = {};
                        while(t = Wt.exec(p)){
                            n[`${t[1].toLowerCase()} `] = (n[`${t[1].toLowerCase()} `] || []).concat(t[2]);
                        }
                    }
                    t = n[`${e.toLowerCase()} `];
                }
                if (t == null) {
                    return null;
                }
                return t.join(", ");
            },
            getAllResponseHeaders: function() {
                if (h) {
                    return p;
                }
                return null;
            },
            setRequestHeader: function(e, t) {
                if (h == null) {
                    e = s[e.toLowerCase()] = s[e.toLowerCase()] || e;
                    a[e] = t;
                }
                return this;
            },
            overrideMimeType: function(e) {
                if (h == null) {
                    v.mimeType = e;
                }
                return this;
            },
            statusCode: function(e) {
                let t;
                if (e) {
                    if (h) {
                        T.always(e[T.status]);
                    } else {
                        for(t in e){
                            w[t] = [
                                w[t],
                                e[t]
                            ];
                        }
                    }
                }
                return this;
            },
            abort: function(e) {
                const t = e || u;
                if (c) {
                    c.abort(t);
                }
                l(0, t);
                return this;
            }
        };
        x.promise(T);
        v.url = `${e || v.url || ie_location.href}`.replace($t, `${ie_location.protocol}//`);
        v.type = t.method || t.type || v.method || v.type;
        v.dataTypes = (v.dataType || "*").toLowerCase().match(D) || [
            ""
        ];
        if (v.crossDomain == null) {
            r = ie_document.createElement("a");
            try {
                r.href = v.url;
                r.href = r.href;
                v.crossDomain = `${Xt.protocol}//${Xt.host}` != `${r.protocol}//${r.host}`;
            } catch (e) {
                v.crossDomain = true;
            }
        }
        if (v.data && v.processData && typeof v.data !== "string") {
            v.data = ce.param(v.data, v.traditional);
        }
        Vt(Bt, v, t, T);
        if (h) {
            return T;
        }
        if ((g = ce.event && v.global) && ce.active++ == 0) {
            ce.event.trigger("ajaxStart");
        }
        v.type = v.type.toUpperCase();
        v.hasContent = !Ft.test(v.type);
        f = v.url.replace(Rt, "");
        if (v.hasContent) {
            if (v.data && v.processData && (v.contentType || "").indexOf("application/x-www-form-urlencoded") === 0) {
                v.data = v.data.replace(Mt, "+");
            }
        } else {
            o = v.url.slice(f.length);
            if (v.data && (v.processData || typeof v.data === "string")) {
                f += (At.test(f) ? "&" : "?") + v.data;
                delete v.data;
            }
            if (v.cache === false) {
                f = f.replace(It, "$1");
                o = `${At.test(f) ? "&" : "?"}_=${jt.guid++}${o}`;
            }
            v.url = f + o;
        }
        if (v.ifModified) {
            if (ce.lastModified[f]) {
                T.setRequestHeader("If-Modified-Since", ce.lastModified[f]);
            }
            if (ce.etag[f]) {
                T.setRequestHeader("If-None-Match", ce.etag[f]);
            }
        }
        if (v.data && v.hasContent && v.contentType !== false || t.contentType) {
            T.setRequestHeader("Content-Type", v.contentType);
        }
        T.setRequestHeader("Accept", v.dataTypes[0] && v.accepts[v.dataTypes[0]] ? v.accepts[v.dataTypes[0]] + (v.dataTypes[0] !== "*" ? `, ${zt}; q=0.01` : "") : v.accepts["*"]);
        for(i in v.headers){
            T.setRequestHeader(i, v.headers[i]);
        }
        if (v.beforeSend && (v.beforeSend.call(y, T, v) === false || h)) {
            return T.abort();
        }
        u = "abort";
        b.add(v.complete);
        T.done(v.success);
        T.fail(v.error);
        if (c = Vt(_t, v, t, T)) {
            T.readyState = 1;
            if (g) {
                m.trigger("ajaxSend", [
                    T,
                    v
                ]);
            }
            if (h) {
                return T;
            }
            if (v.async && v.timeout > 0) {
                d = ie.setTimeout(function() {
                    T.abort("timeout");
                }, v.timeout);
            }
            try {
                h = false;
                c.send(a, l);
            } catch (error) {
                if (h) {
                    throw error;
                }
                l(-1, error);
            }
        } else {
            l(-1, "No Transport");
        }
        function l(e, t, n, r) {
            let i;
            let o;
            let a;
            let s;
            let u;
            let l = t;
            if (!h) {
                h = true;
                if (d) {
                    ie.clearTimeout(d);
                }
                c = undefined;
                p = r || "";
                T.readyState = e > 0 ? 4 : 0;
                i = e >= 200 && e < 300 || e === 304;
                if (n) {
                    s = ((e, t, n)=>{
                        let r;
                        let i;
                        let o;
                        let a;
                        const { contents, dataTypes } = e;
                        while(dataTypes[0] === "*"){
                            dataTypes.shift();
                            if (r === undefined) {
                                r = e.mimeType || t.getResponseHeader("Content-Type");
                            }
                        }
                        if (r) {
                            for(i in contents){
                                if (contents[i] && contents[i].test(r)) {
                                    dataTypes.unshift(i);
                                    break;
                                }
                            }
                        }
                        if (dataTypes[0] in n) {
                            o = dataTypes[0];
                        } else {
                            for(i in n){
                                if (!dataTypes[0] || e.converters[`${i} ${dataTypes[0]}`]) {
                                    o = i;
                                    break;
                                }
                                if (!a) {
                                    a = i;
                                }
                            }
                            o = o || a;
                        }
                        if (o) {
                            if (o !== dataTypes[0]) {
                                dataTypes.unshift(o);
                            }
                            return n[o];
                        }
                    })(v, T, n);
                }
                if (!i && ce.inArray("script", v.dataTypes) > -1 && ce.inArray("json", v.dataTypes) < 0) {
                    v.converters["text script"] = function() {};
                }
                s = ((e, t, n, r)=>{
                    let i;
                    let o;
                    let a;
                    let s;
                    let u;
                    const l = {};
                    const c = e.dataTypes.slice();
                    if (c[1]) {
                        for(a in e.converters){
                            l[a.toLowerCase()] = e.converters[a];
                        }
                    }
                    o = c.shift();
                    while(o){
                        if (e.responseFields[o]) {
                            n[e.responseFields[o]] = t;
                        }
                        if (!u && r && e.dataFilter) {
                            t = e.dataFilter(t, e.dataType);
                        }
                        u = o;
                        if (o = c.shift()) {
                            if (o === "*") {
                                o = u;
                            } else if (u !== "*" && u !== o) {
                                if (!(a = l[`${u} ${o}`] || l[`* ${o}`])) {
                                    for(i in l){
                                        if ((s = i.split(" "))[1] === o && (a = l[`${u} ${s[0]}`] || l[`* ${s[0]}`])) {
                                            if (a === true) {
                                                a = l[i];
                                            } else if (l[i] !== true) {
                                                o = s[0];
                                                c.unshift(s[1]);
                                            }
                                            break;
                                        }
                                    }
                                }
                                if (a !== true) {
                                    if (a && e.throws) {
                                        t = a(t);
                                    } else {
                                        try {
                                            t = a(t);
                                        } catch (error) {
                                            return {
                                                state: "parsererror",
                                                error: a ? error : `No conversion from ${u} to ${o}`
                                            };
                                        }
                                    }
                                }
                            }
                        }
                    }
                    return {
                        state: "success",
                        data: t
                    };
                })(v, s, T, i);
                if (i) {
                    if (v.ifModified) {
                        if (u = T.getResponseHeader("Last-Modified")) {
                            ce.lastModified[f] = u;
                        }
                        if (u = T.getResponseHeader("etag")) {
                            ce.etag[f] = u;
                        }
                    }
                    if (e === 204 || v.type === "HEAD") {
                        l = "nocontent";
                    } else if (e === 304) {
                        l = "notmodified";
                    } else {
                        l = s.state;
                        o = s.data;
                        i = !(a = s.error);
                    }
                } else {
                    a = l;
                    if (!(!e && l)) {
                        l = "error";
                        if (e < 0) {
                            e = 0;
                        }
                    }
                }
                T.status = e;
                T.statusText = `${t || l}`;
                if (i) {
                    x.resolveWith(y, [
                        o,
                        l,
                        T
                    ]);
                } else {
                    x.rejectWith(y, [
                        T,
                        l,
                        a
                    ]);
                }
                T.statusCode(w);
                w = undefined;
                if (g) {
                    m.trigger(i ? "ajaxSuccess" : "ajaxError", [
                        T,
                        v,
                        i ? o : a
                    ]);
                }
                b.fireWith(y, [
                    T,
                    l
                ]);
                if (g) {
                    m.trigger("ajaxComplete", [
                        T,
                        v
                    ]);
                    if (!--ce.active) {
                        ce.event.trigger("ajaxStop");
                    }
                }
            }
        }
        return T;
    },
    getJSON: function(e, t, n) {
        return ce.get(e, t, n, "json");
    },
    getScript: function(e, t) {
        return ce.get(e, undefined, t, "script");
    }
});
ce.each([
    "get",
    "post"
], function(e, i) {
    ce[i] = function(e, t, success, dataType) {
        if (v(t)) {
            dataType = dataType || success;
            success = t;
            t = undefined;
        }
        return ce.ajax(ce.extend({
            url: e,
            type: i,
            dataType,
            data: t,
            success
        }, ce.isPlainObject(e) && e));
    };
});
ce.ajaxPrefilter(function(e) {
    let t;
    for(t in e.headers){
        if (t.toLowerCase() === "content-type") {
            e.contentType = e.headers[t] || "";
        }
    }
});
ce._evalUrl = function(url, t, n) {
    return ce.ajax({
        url,
        type: "GET",
        dataType: "script",
        cache: true,
        async: false,
        global: false,
        converters: {
            "text script": function() {}
        },
        dataFilter: function(e) {
            ce.globalEval(e, t, n);
        }
    });
};
ce.fn.extend({
    wrapAll: function(e) {
        let t;
        if (this[0]) {
            if (v(e)) {
                e = e.call(this[0]);
            }
            t = ce(e, this[0].ownerDocument).eq(0).clone(true);
            if (this[0].parentNode) {
                t.insertBefore(this[0]);
            }
            t.map(function() {
                let e = this;
                while(e.firstElementChild){
                    e = e.firstElementChild;
                }
                return e;
            }).append(this);
        }
        return this;
    },
    wrapInner: function(n) {
        if (v(n)) {
            return this.each(function(e) {
                ce(this).wrapInner(n.call(this, e));
            });
        }
        return this.each(function() {
            const e = ce(this);
            const t = e.contents();
            if (t.length) {
                t.wrapAll(n);
            } else {
                e.append(n);
            }
        });
    },
    wrap: function(t) {
        const n = v(t);
        return this.each(function(e) {
            ce(this).wrapAll(n ? t.call(this, e) : t);
        });
    },
    unwrap: function(e) {
        this.parent(e).not("body").each(function() {
            ce(this).replaceWith(this.childNodes);
        });
        return this;
    }
});
ce.expr.pseudos.hidden = function(e) {
    return !ce.expr.pseudos.visible(e);
};
ce.expr.pseudos.visible = function(e) {
    return !!(e.offsetWidth || e.offsetHeight || e.getClientRects().length);
};
ce.ajaxSettings.xhr = function() {
    try {
        return new ie.XMLHttpRequest;
    } catch (e) {}
};
const Yt = {
    0: 200,
    1223: 204
};
let Qt = ce.ajaxSettings.xhr();
support.cors = !!Qt && "withCredentials" in Qt;
support.ajax = Qt = !!Qt;
ce.ajaxTransport(function(i) {
    let o;
    let a;
    if (support.cors || Qt && !i.crossDomain) {
        return {
            send: function(e, t) {
                let n;
                const r = i.xhr();
                r.open(i.type, i.url, i.async, i.username, i.password);
                if (i.xhrFields) {
                    for(n in i.xhrFields){
                        r[n] = i.xhrFields[n];
                    }
                }
                if (i.mimeType && r.overrideMimeType) {
                    r.overrideMimeType(i.mimeType);
                }
                if (!(i.crossDomain || e["X-Requested-With"])) {
                    e["X-Requested-With"] = "XMLHttpRequest";
                }
                for(n in e){
                    r.setRequestHeader(n, e[n]);
                }
                o = function(e) {
                    return function() {
                        if (o) {
                            o = a = r.onload = r.onerror = r.onabort = r.ontimeout = r.onreadystatechange = null;
                            switch(e){
                                case "abort":
                                    r.abort();
                                    break;
                                case "error":
                                    if (typeof r.status !== "number") {
                                        t(0, "error");
                                    } else {
                                        t(r.status, r.statusText);
                                    }
                                    break;
                                default:
                                    t(Yt[r.status] || r.status, r.statusText, (r.responseType || "text") !== "text" || typeof r.responseText !== "string" ? {
                                        binary: r.response
                                    } : {
                                        text: r.responseText
                                    }, r.getAllResponseHeaders());
                            }
                        }
                    };
                };
                r.onload = o();
                a = r.onerror = r.ontimeout = o("error");
                if (r.onabort !== undefined) {
                    r.onabort = a;
                } else {
                    r.onreadystatechange = function() {
                        if (r.readyState === 4) {
                            ie.setTimeout(function() {
                                if (o) {
                                    a();
                                }
                            });
                        }
                    };
                }
                o = o("abort");
                try {
                    r.send(i.hasContent && i.data || null);
                } catch (error) {
                    if (o) {
                        throw error;
                    }
                }
            },
            abort: function() {
                if (o) {
                    o();
                }
            }
        };
    }
});
ce.ajaxPrefilter(function(e) {
    if (e.crossDomain) {
        e.contents.script = false;
    }
});
ce.ajaxSetup({
    accepts: {
        script: "text/javascript, application/javascript, application/ecmascript, application/x-ecmascript"
    },
    contents: {
        script: /\b(?:java|ecma)script\b/
    },
    converters: {
        "text script": function(e) {
            ce.globalEval(e);
            return e;
        }
    }
});
ce.ajaxPrefilter("script", function(e) {
    if (e.cache === undefined) {
        e.cache = false;
    }
    if (e.crossDomain) {
        e.type = "GET";
    }
});
ce.ajaxTransport("script", function(n) {
    let r;
    let i;
    if (n.crossDomain || n.scriptAttrs) {
        return {
            send: function(e, t) {
                r = ce("<script>").attr(n.scriptAttrs || {}).prop({
                    charset: n.scriptCharset,
                    src: n.url
                }).on("load error", i = function(e) {
                    r.remove();
                    i = null;
                    if (e) {
                        t(e.type === "error" ? 404 : 200, e.type);
                    }
                });
                ie_document.head.appendChild(r[0]);
            },
            abort: function() {
                if (i) {
                    i();
                }
            }
        };
    }
});
let Jt;
const Kt = [];
const Zt = /(=)\?(?=&|$)|\?\?/;
ce.ajaxSetup({
    jsonp: "callback",
    jsonpCallback: function() {
        const e = Kt.pop() || `${ce.expando}_${jt.guid++}`;
        this[e] = true;
        return e;
    }
});
ce.ajaxPrefilter("json jsonp", function(e, t, n) {
    let r;
    let i;
    let o;
    const a = e.jsonp !== false && (Zt.test(e.url) ? "url" : typeof e.data === "string" && (e.contentType || "").indexOf("application/x-www-form-urlencoded") === 0 && Zt.test(e.data) && "data");
    if (a || e.dataTypes[0] === "jsonp") {
        r = e.jsonpCallback = v(e.jsonpCallback) ? e.jsonpCallback() : e.jsonpCallback;
        if (a) {
            e[a] = e[a].replace(Zt, `\$1${r}`);
        } else if (e.jsonp !== false) {
            e.url += `${(At.test(e.url) ? "&" : "?") + e.jsonp}=${r}`;
        }
        e.converters["script json"] = function() {
            if (!o) {
                ce.error(`${r} was not called`);
            }
            return o[0];
        };
        e.dataTypes[0] = "json";
        i = ie[r];
        ie[r] = function() {
            o = arguments;
        };
        n.always(function() {
            if (i === undefined) {
                ce(ie).removeProp(r);
            } else {
                ie[r] = i;
            }
            if (e[r]) {
                e.jsonpCallback = t.jsonpCallback;
                Kt.push(r);
            }
            if (o && v(i)) {
                i(o[0]);
            }
            i = undefined;
            o = undefined;
        });
        return "script";
    }
});
support.createHTMLDocument = ((Jt = ie_document.implementation.createHTMLDocument("").body).innerHTML = "<form></form><form></form>", Jt.childNodes.length === 2);
ce.parseHTML = function(e, t, n) {
    if (typeof e !== "string") {
        return [];
    }
    if (typeof t === "boolean") {
        n = t;
        t = false;
    }
    if (!t) {
        if (support.createHTMLDocument) {
            (r = (t = ie_document.implementation.createHTMLDocument("")).createElement("base")).href = ie_document.location.href;
            t.head.appendChild(r);
        } else {
            t = ie_document;
        }
    }
    o = !n && [];
    if (i = w.exec(e)) {
        return [
            t.createElement(i[1])
        ];
    }
    return i = Ae([
        e
    ], t, o), o && o.length && ce(o).remove(), ce.merge([], i.childNodes);
    var r;
    var i;
    var o;
};
ce.fn.load = function(e, t, n) {
    let r;
    let i;
    let o;
    const a = this;
    const s = e.indexOf(" ");
    if (s > -1) {
        r = Tt(e.slice(s));
        e = e.slice(0, s);
    }
    if (v(t)) {
        n = t;
        t = undefined;
    } else if (t && typeof t === "object") {
        i = "POST";
    }
    if (a.length > 0) {
        ce.ajax({
            url: e,
            type: i || "GET",
            dataType: "html",
            data: t
        }).done(function(e) {
            o = arguments;
            a.html(r ? ce("<div>").append(ce.parseHTML(e)).find(r) : e);
        }).always(n && function(e, t) {
            a.each(function() {
                n.apply(this, o || [
                    e.responseText,
                    t,
                    e
                ]);
            });
        });
    }
    return this;
};
ce.expr.pseudos.animated = function(t) {
    return ce.grep(ce.timers, function(e) {
        return t === e.elem;
    }).length;
};
ce.offset = {
    setOffset: function(e, t, n) {
        let r;
        let i;
        let o;
        let a;
        let s;
        let u;
        const l = ce.css(e, "position");
        const c = ce(e);
        const f = {};
        if (l === "static") {
            e.style.position = "relative";
        }
        s = c.offset();
        o = ce.css(e, "top");
        u = ce.css(e, "left");
        if ((l === "absolute" || l === "fixed") && (o + u).indexOf("auto") > -1) {
            a = (r = c.position()).top;
            i = r.left;
        } else {
            a = parseFloat(o) || 0;
            i = parseFloat(u) || 0;
        }
        if (v(t)) {
            t = t.call(e, n, ce.extend({}, s));
        }
        if (t.top != null) {
            f.top = t.top - s.top + a;
        }
        if (t.left != null) {
            f.left = t.left - s.left + i;
        }
        if ("using" in t) {
            t.using.call(e, f);
        } else {
            c.css(f);
        }
    }
};
ce.fn.extend({
    offset: function(t) {
        if (arguments.length) {
            if (t === undefined) {
                return this;
            }
            return this.each(function(e) {
                ce.offset.setOffset(this, t, e);
            });
        }
        let e;
        let n;
        const r = this[0];
        if (r) {
            if (r.getClientRects().length) {
                e = r.getBoundingClientRect();
                n = r.ownerDocument.defaultView;
                return {
                    top: e.top + n.pageYOffset,
                    left: e.left + n.pageXOffset
                };
            }
            return {
                top: 0,
                left: 0
            };
        }
    },
    position: function() {
        if (this[0]) {
            let e;
            let t;
            let n;
            const r = this[0];
            let i = {
                top: 0,
                left: 0
            };
            if (ce.css(r, "position") === "fixed") {
                t = r.getBoundingClientRect();
            } else {
                t = this.offset();
                n = r.ownerDocument;
                e = r.offsetParent || n.documentElement;
                while(e && (e === n.body || e === n.documentElement) && ce.css(e, "position") === "static"){
                    e = e.parentNode;
                }
                if (e && e !== r && e.nodeType === 1) {
                    i = ce(e).offset();
                    i.top += ce.css(e, "borderTopWidth", true);
                    i.left += ce.css(e, "borderLeftWidth", true);
                }
            }
            return {
                top: t.top - i.top - ce.css(r, "marginTop", true),
                left: t.left - i.left - ce.css(r, "marginLeft", true)
            };
        }
    },
    offsetParent: function() {
        return this.map(function() {
            let offsetParent = this.offsetParent;
            while(offsetParent && ce.css(offsetParent, "position") === "static"){
                offsetParent = offsetParent.offsetParent;
            }
            return offsetParent || C_documentElement;
        });
    }
});
ce.each({
    scrollLeft: "pageXOffset",
    scrollTop: "pageYOffset"
}, function(t, i) {
    const o = i === "pageYOffset";
    ce.fn[t] = function(e) {
        return M(this, function(e, t, n) {
            let r;
            if (y(e)) {
                r = e;
            } else if (e.nodeType === 9) {
                r = e.defaultView;
            }
            if (n === undefined) {
                if (r) {
                    return r[i];
                }
                return e[t];
            }
            if (r) {
                r.scrollTo(o ? r.pageXOffset : n, o ? n : r.pageYOffset);
            } else {
                e[t] = n;
            }
        }, t, e, arguments.length);
    };
});
ce.each([
    "top",
    "left"
], function(e, n) {
    ce.cssHooks[n] = Ye(support.pixelPosition, function(e, t) {
        if (t) {
            t = Ge(e, n);
            if (_e.test(t)) {
                return `${ce(e).position()[n]}px`;
            }
            return t;
        }
    });
});
ce.each({
    Height: "height",
    Width: "width"
}, function(a, content) {
    ce.each({
        padding: `inner${a}`,
        content,
        "": `outer${a}`
    }, function(r, o) {
        ce.fn[o] = function(e, t) {
            const n = arguments.length && (r || typeof e !== "boolean");
            const i = r || (e === true || t === true ? "margin" : "border");
            return M(this, function(e, t, n) {
                let r;
                if (y(e)) {
                    if (o.indexOf("outer") === 0) {
                        return e[`inner${a}`];
                    }
                    return e.document.documentElement[`client${a}`];
                }
                if (e.nodeType === 9) {
                    r = e.documentElement;
                    return Math.max(e.body[`scroll${a}`], r[`scroll${a}`], e.body[`offset${a}`], r[`offset${a}`], r[`client${a}`]);
                }
                if (n === undefined) {
                    return ce.css(e, t, i);
                }
                return ce.style(e, t, n, i);
            }, content, n ? e : undefined, n);
        };
    });
});
ce.each([
    "ajaxStart",
    "ajaxStop",
    "ajaxComplete",
    "ajaxError",
    "ajaxSuccess",
    "ajaxSend"
], function(e, t) {
    ce.fn[t] = function(e) {
        return this.on(t, e);
    };
});
ce.fn.extend({
    bind: function(e, t, n) {
        return this.on(e, null, t, n);
    },
    unbind: function(e, t) {
        return this.off(e, null, t);
    },
    delegate: function(e, t, n, r) {
        return this.on(t, e, n, r);
    },
    undelegate: function(e, t, n) {
        if (arguments.length === 1) {
            return this.off(e, "**");
        }
        return this.off(t, e || "**", n);
    },
    hover: function(e, t) {
        return this.on("mouseenter", e).on("mouseleave", t || e);
    }
});
ce.each("blur focus focusin focusout resize scroll click dblclick mousedown mouseup mousemove mouseover mouseout mouseenter mouseleave change select submit keydown keypress keyup contextmenu".split(" "), function(e, n) {
    ce.fn[n] = function(e, t) {
        if (arguments.length > 0) {
            return this.on(n, null, e, t);
        }
        return this.trigger(n);
    };
});
const en = /^[\s\uFEFF\xA0]+|([^\s\uFEFF\xA0])[\s\uFEFF\xA0]+$/g;
ce.proxy = function(e, t) {
    let n;
    let r;
    let i;
    if (typeof t === "string") {
        n = e[t];
        t = e;
        e = n;
    }
    if (v(e)) {
        r = oe_slice.call(arguments, 2);
        i = function() {
            return e.apply(t || this, r.concat(oe_slice.call(arguments)));
        };
        i.guid = e.guid = e.guid || ce.guid++;
        return i;
    }
};
ce.holdReady = function(e) {
    if (e) {
        ce.readyWait++;
    } else {
        ce.ready(true);
    }
};
ce.isArray = Array.isArray;
ce.parseJSON = JSON.parse;
ce.nodeName = fe;
ce.isFunction = v;
ce.isWindow = y;
ce.camelCase = F;
ce.type = x;
ce.now = Date.now;
ce.isNumeric = function(e) {
    const t = ce.type(e);
    return (t === "number" || t === "string") && !isNaN(e - parseFloat(e));
};
ce.trim = function(e) {
    if (e == null) {
        return "";
    }
    return `${e}`.replace(en, "$1");
};
if (typeof define === "function" && define.amd) {
    define("jquery", [], function() {
        return ce;
    });
}
const { jQuery, $: $_1 } = ie;
export default (ce.noConflict = function(e) {
    if (ie.$ === ce) {
        ie.$ = $_1;
    }
    if (e && ie.jQuery === ce) {
        ie.jQuery = jQuery;
    }
    return ce;
}, typeof e === "undefined" && (ie.jQuery = ie.$ = ce), ce);
