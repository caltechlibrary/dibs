<!-- For character codes see https://en.wikipedia.org/wiki/Block_Elements -->
%if get('value', 0) == 0:
<span style="color: #ddd; position: relative; top: 0.05rem">_</span>
%elif get('value', 0) < 75:
▁
%elif get('value', 0) < 150:
▂
%elif get('value', 0) < 300:
▄
%elif get('value', 0) < 500:
▆
%else:
█
%end
