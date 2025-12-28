#!/usr/bin/env python3
"""
测试文件名转小写功能

验证扩展名是否正确转换
"""

def test_lowercase_conversion():
    """测试各种文件名转换"""
    test_cases = [
        # (原始名称, 预期结果)
        ("Dark-Brown.WEBP", "dark-brown.webp"),
        ("Female-White", "female-white"),
        ("Loose-Curls.JPG", "loose-curls.jpg"),
        ("Test-File.PNG", "test-file.png"),
        ("UPPERCASE.WEBP", "uppercase.webp"),
        ("MixedCase.WebP", "mixedcase.webp"),
        ("file.TXT", "file.txt"),
        ("NoExtension", "noextension"),
    ]
    
    print("=" * 60)
    print("🧪 测试文件名转小写")
    print("=" * 60)
    print()
    
    all_passed = True
    
    for original, expected in test_cases:
        result = original.lower()
        passed = result == expected
        
        status = "✅" if passed else "❌"
        print(f"{status} {original:30} -> {result:30} {'(预期: ' + expected + ')' if not passed else ''}")
        
        if not passed:
            all_passed = False
    
    print()
    print("=" * 60)
    if all_passed:
        print("✅ 所有测试通过！")
    else:
        print("❌ 部分测试失败")
    print("=" * 60)


if __name__ == '__main__':
    test_lowercase_conversion()
