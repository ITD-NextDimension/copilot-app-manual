import { Converter } from "opencc-js";

const convert = Converter({ from: "cn", to: "twp" });
const terminology = new Map([
    ["一箇", "一個"], ["只准備", "只準備"], ["賬", "帳"],
    ["許可權", "權限"], ["介面卡", "轉接器"], ["擴充套件", "擴充功能"],
    ["外掛", "擴充功能"], ["指令碼", "腳本"], ["點選", "點擊"],
    ["畫素", "像素"], ["視口", "檢視區"], ["埠", "連接埠"],
    ["全域性", "全域"], ["復制", "複製"], ["重復", "重複"],
    ["同文檔", "同文件"], ["文本", "文字"], ["引數", "參數"],
    ["不是隻", "不是只"], ["併產生", "並產生"], ["豎屏", "直式"],
    ["英寸", "吋"], ["觸控屏", "觸控螢幕"], ["周檢視", "週檢視"],
    ["其他周", "其他週"], ["計算機專業", "資訊相關科系"], ["搜索", "搜尋"],
]);

export function toTraditional(value) {
    let result = convert(value);
    for (const [source, target] of terminology) result = result.replaceAll(source, target);
    return result;
}
